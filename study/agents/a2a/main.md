Kubernetes [Docker + Event Bus]
- Node
    - Docker + Side Card (Stateless)
    - Agent [FastAPI + Agent Framework + Interupt for HITL]
    - Ollama + LLM
    - Public Route for Agent-Card

- Service Mesh
    - Agent Registry and Agent Discovery
    - Event Bus + AuthN + AuthO Service (Stateful)
    - Ingress Queue and Egress Queue
    - MCP Bi-directional + RestAPI + Webhook + Queue Communication
    - VIPER Client-Server Architecutre for Frontend and Backend
    - Parent Agent as RestAPI Service
        - Calls MCP Gateway as Non-Sandbox (Static) [if Local, Stdio Tool Service is here]
        - Calls MCP Gateway as Sandbox (Dynamic) [if Local, Stdio Tool Service is here]
            - Tools as MCP Services in Container, if Remote
        - Calls A2A Gateway as Non-Sandbox (Static) [if Local, Stdio Tool Service is here]
        - Calls A2A Gateway as Sandbox (Dynamic) [if Local, Stdio Tool Service is here]
            - Agents as A2A Services in Container, if Remote

- Storage
    - InComplete Response State Storage

Virtualization
- VM [Infra / Platform]
    - Container [Multi Agent]
        - Sandbox [Single Agent]

- Gives Isolation
    - Cohesion -> Security
    - Decoupling -> Scale 


