Kubernetes [Docker + Event Bus]
- Node
    - Docker + Side Card (Stateless)
    - Agent [FastAPI + Agent Framework + Interupt for HITL]
    - Ollama + LLM
    - Public Route for Agent-Card
    - Dynamic Orchestration using E2B 
        - A controller a center (of Parent Agent) would orchestrate the dynamically create agent service and tool service
        - Sandbox them using a 'Docker + FastAPI Based A2A or MCP Server' Template
        - Deploy it to the Next Pod in Next Node as Per Distribution/Scheduling Algorithm (like Round Robin)
        - Use Service Mesh having Side Cars of Sandboxed A2A Client and MCP Client in form of Gateways in Parent Agent 

- Service Mesh
    - Agent Registry and Agent Discovery
    - Event Bus + AuthN + AuthO Service (Stateful)
    - Ingress Queue and Egress Queue
    - MCP Bi-directional + RestAPI + Webhook + Queue Communication
    - VIPER Client-Server Architecutre for Frontend and Backend
    - Parent Agent as RestAPI Service
        - Calls MCP Gateway as In-Memory (Static) [if Local, Stdio Tool Service is here]
        - Calls MCP Gateway as Sandbox/Fork (Dynamic) [if Local, Stdio Tool Service is here]
            - Tools as MCP Services in Container, if Remote
        - Calls A2A Gateway as In-Memory (Static) [if Local, Stdio Tool Service is here]
        - Calls A2A Gateway as Sandbox/Fork (Dynamic) [if Local, Stdio Tool Service is here]
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


