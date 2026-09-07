# MCP Tutorial — Compact Study Notes (Mukul Raina)

The notes below are based **strictly on the transcript** and cover each distinct concept discussed. 

## 1. Model Context Protocol (MCP)

* MCP is presented as a **standardized, open protocol for connecting AI systems to external data sources**.
* Its main purpose is to eliminate the need for **custom connectors for every AI application ↔ data source combination**.
* It was announced by Anthropic as an open standard, so it is not limited to Anthropic products.

## 2. The N × M Integration Problem

* Traditional architecture requires a custom integration for every combination of AI application and data source.
* With **N AI applications** and **M data sources**, this creates **N × M integrations**.
* MCP changes this to approximately **N + M**:

  * AI applications implement MCP clients.
  * Data sources expose MCP servers.
* Example from the transcript: 3 applications × 10 sources = **30 integrations traditionally**, versus **13 implementations with MCP**. 

## 3. MCP vs. RAG

| RAG                                | MCP                                                     |
| ---------------------------------- | ------------------------------------------------------- |
| Retrieves documents                | Provides structural access to data/functionality        |
| Uses embeddings/vector search      | Uses standardized protocol access                       |
| Primarily document collections     | Live data, tools, APIs, databases, files, event streams |
| Historical knowledge/documentation | Current data and actions                                |

* **RAG:** useful for understanding what happened before.
* **MCP:** useful for accessing what is happening now and performing actions.
* They are **complementary**, not mutually exclusive. 

## 4. MCP Architecture

MCP has three core entities:

### Host

* The **AI application**.
* Initiates connections to MCP servers.
* Manages lifecycle, orchestration, authentication, and permissions.
* Decides which servers to use based on user intent.

### MCP Server

* Acts as a **data/functionality provider**.
* Exposes resources, tools, and prompts through MCP.
* Can run locally or remotely.
* Implementation language does not matter as long as it follows the MCP protocol.

### MCP Client

* Lives inside the host.
* Handles MCP communication and protocol details.
* Uses **JSON-RPC 2.0** messaging.
* Performs capability negotiation.
* Manages request/response lifecycle.

The architecture separates responsibilities: **host = orchestration, server = data/functionality, client = protocol communication**. 

## 5. Stateful Connections & Capability Discovery

* MCP communication uses **stateful connections** that remain open.
* Servers declare what they provide through **capability discovery**.
* Hosts can then consume the capabilities they need.
* This keeps the system modular and separates orchestration from data access.

## 6. MCP Resources

* Resources provide **read-only data access**.
* Examples:

  * File contents
  * Database records
  * API responses
  * GitHub issues
  * Slack messages
* Resources use **URI-based addressing**.
* They can support text/binary content and pagination for large datasets.
* Key characteristic: **passive/read-only** — the model reads the data but does not modify it through the resource.

## 7. MCP Tools

* Tools are **executable functions** that the model can invoke to perform actions.
* Examples:

  * Create a GitHub issue
  * Send an email
  * Update a database record
* Tools define their inputs using **JSON Schema**.
* They return structured results to the model.
* In production, tool execution typically requires **explicit user approval** for potentially consequential actions.

## 8. MCP Prompts

* Prompts are **reusable templates with placeholders**.
* Examples include templates for:

  * Security analysis of a codebase
  * Summarizing recent Slack activity
* They reduce repeated prompt-engineering work.
* They provide consistency and can dynamically reference resources.

### Core distinction

> **Resources = passive data**
> **Tools = active operations**
> **Prompts = reusable workflow templates** 

---

# Production Patterns

## 9. Authentication

* For third-party services such as GitHub or Google Drive, the transcript recommends **OAuth 2.0** with token-based authentication and user consent.
* For internal systems, **API keys** can be used.
* API keys should have rotation policies, with the transcript suggesting **90 days or less**.

## 10. Scope-Based Permissions / Least Privilege

* Give an MCP server only the permissions it actually needs.
* Example: if it only needs to read GitHub issues, don't give it write access.
* Restricting permissions reduces the attack surface.

## 11. Tool Execution Logging

Log tool executions with:

* User context
* Timestamp
* Parameters

This audit trail helps with:

* Compliance
* Debugging
* Security investigations

## 12. Rate Limiting

* Apply rate limits **per server and per user**.
* Example from the transcript: 100 requests/minute/server/user.
* Protects against abuse, runaway costs, and bugs.

---

# Deployment

## 13. Local MCP Servers

* Run on the developer's local machine.
* Advantages:

  * Fast iteration
  * No network latency
* Limited to local resources.
* Configuration is done through a JSON file.
* Suitable for development/testing rather than production.

## 14. Remote MCP Servers

* Centralized cloud deployments.
* Examples of infrastructure mentioned:

  * Azure Container Instances
  * AWS ECS
  * Kubernetes
* Require authentication.
* Support horizontal scaling.
* For high traffic, multiple instances can run behind a load balancer.
* Autoscaling can handle traffic spikes.

## 15. Hybrid Deployment

* Combine local and remote servers.
* Sensitive/critical data → **remote authenticated servers**.
* Non-sensitive/public data → potentially **local servers**.
* Goal: balance security and latency.

---

# Reliability & Failure Handling

## 16. Graceful Degradation

* If an MCP server becomes unavailable, the AI application should continue functioning with reduced capabilities rather than completely failing.

## 17. Timeouts

* Configure timeouts per server.
* Transcript gives **5–30 seconds** as a typical production range depending on the operation.

## 18. Exponential Backoff

For transient failures, progressively increase retry delays:

**1 sec → 2 sec → 4 sec → 8 sec → ...**

* Prevents overwhelming an already-failing server.

## 19. Fallback Data Sources

* When possible, use an alternative source if the primary source fails.
* Example: serve slightly stale cached data if the primary database is unavailable.
* Keeps the system functional despite individual component failures.

---

# MCP + Existing AI Workflows

## 20. MCP + RAG Hybrid Pattern

* MCP supplies **live/structural information**.
* RAG supplies **historical/documentary context**.
* Together:

  * MCP answers: **“What's happening now?”**
  * RAG answers: **“What happened before?”**

Example:

* MCP → current customer-support ticket status, assignment, updates.
* RAG → historical knowledge-base solutions for similar issues.

## 21. Multi-Server Orchestration

* A production AI application may connect to **5–15 MCP servers**.
* Examples:

  * GitHub
  * Jira
  * Slack
  * PostgreSQL
* The model chooses which server(s) to query based on user intent.

## 22. Parallel Server Requests

* Multiple servers can be queried simultaneously to reduce latency.
* Example: answering "What are my action items today?" could involve querying email, calendar, GitHub, and Slack in parallel.
* However, too much data should not be sent to the model at once.

---

# Cost & Performance Optimization

## 23. Caching

* Cache frequently accessed data.
* Set TTL according to freshness requirements.
* Example from transcript:

  * User profiles → potentially cached for 5 minutes.
  * Real-time stock prices → little or no caching.

## 24. Lazy Loading

* Fetch resources **only when explicitly requested** by the model.
* Avoid unnecessarily prefetching everything.

## 25. Batching

* Batch requests where possible to improve efficiency.

## 26. Latency Monitoring & Circuit Breakers

* Monitor latency for each server.
* Fail fast when servers are too slow.
* If a server repeatedly exceeds timeout thresholds, consider temporarily applying a **circuit breaker**.

---

# Migration to MCP

## 27. Migrating Existing Custom Integrations

Recommended approach:

1. Identify existing custom connectors:

   * Slack bots
   * GitHub API wrappers
   * Database helpers
   * etc.
2. **Wrap the existing logic** inside MCP servers instead of rewriting everything.
3. Run MCP alongside the legacy integrations.
4. Gradually shift traffic:

   * 10%
   * 50%
   * 90%
   * 100%
5. Deprecate the old integrations only after MCP is proven to work.

This provides a **gradual rollout and rollback path** while reducing maintenance burden over time. 

---

# Monitoring & Observability

## 28. Server Health & Response Time

* Track server availability.
* Monitor response times.
* Build dashboards showing which servers are up and how quickly they respond.

## 29. Tool Execution Observability

* Log tool executions together with user context.
* Monitor authentication failures and rate-limit hits.
* Configure alerts around important failure/security signals.

## 30. Model Decision Quality

Monitor whether the model:

* Selects the correct MCP server.
* Selects the correct tool.
* Makes appropriate decisions for requests.

Also track **user corrections** to identify where the system needs improvement.

---

# 31. Overall Adoption Strategy

* MCP can reduce integration complexity when AI applications need access to multiple data sources.
* Start small with **one or two servers**.
* Validate that they work well.
* Expand gradually.
* **Do not migrate everything at once.** 