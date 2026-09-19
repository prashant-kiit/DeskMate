### References:
- https://www.youtube.com/watch?v=yFIF5O7daHI
- https://www.youtube.com/watch?v=kU8Tg1_PYJE
- https://code.claude.com/docs/en/how-claude-code-works
- https://www.youtube.com/watch?v=Lu1UWqVTbQg : https://github.com/avbiswas/neural-code/tree/main/neuralcode
- 

### Architecture:
- Supervision Agent -> Sub-Agents + Tools (ACL using Permission List + Sandbox)
- Agent Loop + Event Loop + State Events and Listers + KV Prefix Cache (ReAct + Observer the Output or Error of Tool/Agent)
- For Each Loop : User + System + Assistant + Tool Prompt as Context with Context Capping using Pydantic Schema & Summazier Model
- Major Static Tools: Read File, Write/Update File, Bash CMD, CURL CMD (Browser CMD Using Headless Browser)
- Major Static Sub Agents: Designer, Planner (Plan/Todos [COT Loop - Observer_Reason_Action_Repeat] & Execute), Arcitect, Implementer, Tester (Self-Relexion), Deployer
- Has scope for Dynamic Agents and Tools in AI Sandbox
- Memory : Conversation (Session + Episodic [LLM + Regex based Dream Job based on Relevancy & Recency] ), User & Tool/Agent Memory, Procedural [Working Flow + Non Working Flow] Memory, State Memory (Checkpoints For Rollback + Version Control using Checkpoint_ID + Content_ID + Hashes + Version_Vector + DateTime), Log Memory
- Handle /SKILL.md and /AGENT.md in User CLI by extracting the Content as User Prompt, Otherwise Read the MetaData at the top of all SKILL.md and AGENT.md in inject in System Prompt (Like any In-Memory Tool or Agent)
- Use Late Injection in Sequence of Prompts Array (Prompts Chain) for State Detection/Updation (Checkpoint) for Plan/Todo Progress
