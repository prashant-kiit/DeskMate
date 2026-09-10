# AI Agent Architecture: Docker + A2A + MCP + Sandbox

A concise practical tutorial for a **Parent Agent** that uses an LLM to generate caller code, then executes that untrusted code inside an **E2B Sandbox** to communicate with separate **A2A Agent** and **MCP Tool** services.

## 1. Architecture

```text
                         User
                           |
                           v
                  +------------------+
                  |  Parent Agent    |
                  |  FastAPI :8000   |
                  |       + LLM      |
                  +--------+---------+
                           |
              generates caller programs
                    +------+------+
                    |             |
                 A2A code       MCP code
                    |             |
                    v             v
              +-------------------------+
              |       E2B Sandbox       |
              |                         |
              |  a2a_call.py            |
              |  mcp_call.py            |
              +----------+------+-------+
                         |      |
                       A2A|      |MCP
                         v      v
                 +---------+  +---------+
                 |  Side   |  |  Side   |
                 | Agent   |  |  Tool   |
                 | :8001   |  | :8002   |
                 +---------+  +---------+
```

- **A2A** = agent-to-agent communication
- **MCP** = agent-to-tool communication
- **Sandbox** = isolated environment for executing LLM-generated code
- **Docker** = packages and runs each service independently

## 2. Services

```text
parent      :8000
side-agent  :8001
side-tool   :8002
```

Project:

```text
multi-agent/
├── parent/main.py
├── side-agent/main.py
├── side-tool/main.py
└── docker-compose.yml
```

## 3. Side Agent: A2A

Simplified A2A endpoint:

```python
# side-agent/main.py

from fastapi import FastAPI

app = FastAPI()

@app.post("/a2a")
async def a2a(request: dict):
    task = request["message"]

    return {
        "status": "completed",
        "result": f"Side Agent processed: {task}"
    }
```

Run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

For production, use the A2A SDK/protocol rather than this simplified endpoint.

## 4. Side Tool: MCP

```python
# side-tool/main.py

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math Tools")

@mcp.tool()
def calculate_sum(numbers: list[int]) -> int:
    return sum(numbers)
```

Conceptual MCP endpoint:

```text
http://side-tool:8002/mcp
```

Use a supported MCP transport such as Streamable HTTP in production.

## 5. LLM Generates Caller Programs

The Parent Agent asks the LLM to generate two programs.

### A2A caller

```python
# a2a_call.py

import httpx

response = httpx.post(
    "https://side-agent.example.com/a2a",
    json={"message": "Analyze the sales data"}
)

print(response.json())
```

### MCP caller

```python
# mcp_call.py

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():

    async with streamable_http_client(
        "https://side-tool.example.com/mcp"
    ) as streams:

        async with ClientSession(*streams) as session:

            await session.initialize()

            result = await session.call_tool(
                "calculate_sum",
                {"numbers": [10, 20, 30, 40]}
            )

            print(result)

asyncio.run(main())
```

Important:

```text
LLM generates code
       |
       v
   E2B Sandbox
       |
       v
    execute
```

Do not execute generated code directly in the Parent process.

## 6. Parent Agent + LLM

Install:

```bash
pip install openai e2b-code-interpreter
```

Environment:

```bash
export OPENAI_API_KEY="..."
export E2B_API_KEY="..."
```

```python
# parent/main.py

from fastapi import FastAPI
from openai import OpenAI
from e2b_code_interpreter import Sandbox

app = FastAPI()
llm = OpenAI()

def generate_code():

    prompt = """
Generate two Python programs.

A2A:
Call https://side-agent.example.com/a2a
with: "Analyze sales data"

MCP:
Connect to https://side-tool.example.com/mcp
and call calculate_sum with [10,20,30,40]

Return:

---A2A---
<code>

---MCP---
<code>
"""

    response = llm.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    output = response.output_text

    a2a_code = (
        output.split("---A2A---")[1]
        .split("---MCP---")[0]
        .strip()
    )

    mcp_code = (
        output.split("---MCP---")[1]
        .strip()
    )

    return a2a_code, mcp_code
```

## 7. Execute Generated Code in E2B

Never:

```python
exec(a2a_code)
exec(mcp_code)
```

inside the Parent Agent.

Instead:

```python
def execute_in_sandbox(a2a_code, mcp_code):

    with Sandbox() as sandbox:

        sandbox.files.write(
            "/tmp/a2a_call.py",
            a2a_code
        )

        sandbox.files.write(
            "/tmp/mcp_call.py",
            mcp_code
        )

        a2a_result = sandbox.run_code(
            'exec(open("/tmp/a2a_call.py").read())'
        )

        mcp_result = sandbox.run_code(
            'exec(open("/tmp/mcp_call.py").read())'
        )

        return {
            "a2a": a2a_result.text,
            "mcp": mcp_result.text
        }
```

## 8. Complete Parent Endpoint

```python
@app.post("/run")
async def run():

    # 1. LLM generates caller code
    a2a_code, mcp_code = generate_code()

    # 2. Execute generated code in sandbox
    result = execute_in_sandbox(
        a2a_code,
        mcp_code
    )

    # 3. Return results
    return result
```

## 9. Docker Compose

```yaml
services:

  parent:
    build: ./parent
    ports:
      - "8000:8000"

  side-agent:
    build: ./side-agent
    ports:
      - "8001:8001"

  side-tool:
    build: ./side-tool
    ports:
      - "8002:8002"
```

Inside Docker:

```text
parent
  |
  +--> http://side-agent:8001
  |
  +--> http://side-tool:8002
```

But E2B is external to the Docker network. Therefore the sandbox normally cannot resolve:

```text
http://side-agent:8001
http://side-tool:8002
```

Expose the required services through authenticated HTTPS endpoints, or use an appropriate network bridge/tunnel for development.

## 10. Docker vs Sandbox

| Technology | Purpose |
|---|---|
| Docker | Run isolated application services |
| Sandbox | Safely execute dynamic/untrusted code |
| E2B | Managed cloud sandbox for AI/code execution |
| A2A | Agent ↔ Agent communication |
| MCP | Agent ↔ Tool communication |
| FastAPI | API layer |
| LLM | Reasoning/code generation |

Typical deployment:

```text
Docker
├── Parent Agent
├── Side Agent
└── Side Tool

E2B
└── Temporary execution environment
    ├── generated A2A caller
    └── generated MCP caller
```

## 11. End-to-End Flow

```text
1. User
      |
2. Parent Agent
      |
3. LLM generates A2A + MCP caller code
      |
4. E2B Sandbox
      |
      +---- A2A ----> Side Agent
      |
      +---- MCP ----> Side Tool
      |
5. Results
      |
6. Parent Agent / LLM
      |
7. Final Answer
```

## 12. Why Sandbox?

Without sandbox:

```text
LLM
 |
 | generated Python
 v
Parent Process
 |
 +-- exec(code)       <-- risky
```

With sandbox:

```text
LLM
 |
 | generated Python
 v
E2B Sandbox
 |
 +-- isolated execution
 +-- filesystem
 +-- packages
 +-- resource limits
 |
 v
result
```

The sandbox prevents generated code from executing directly inside the Parent Agent process.

## 13. Production Safety

Do not blindly allow LLM-generated:

```text
URLs
imports
shell commands
file paths
credentials
network destinations
```

Prefer constrained APIs:

```python
call_agent("side_agent", task)
call_tool("calculate_sum", numbers)
```

Enforce:

```text
Network allowlist
+
Package allowlist
+
Filesystem restrictions
+
CPU/memory limits
+
Execution timeout
+
No production credentials
+
Authentication
```

The LLM decides **what it wants to call**; the runtime decides **what it is actually allowed to execute**.

## 14. Core Mental Model

```text
                LLM
                 |
          generates code
                 |
                 v
          +-------------+
          |   Sandbox   |
          +------+------+
                 |
        executes caller code
          /              \
         /                \
       A2A                MCP
        |                  |
        v                  v
   Side Agent          Side Tool
```

- **A2A:** How does one agent communicate with another agent?
- **MCP:** How does an agent communicate with a tool?
- **Sandbox:** Where can generated code safely execute?
- **Docker:** How are the independent services packaged and deployed?

Together:

**LLM + Sandbox + Docker + A2A + MCP = dynamically composed, isolated AI-agent architecture.**
