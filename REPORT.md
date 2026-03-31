# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Q1: "What is the agentic loop?"**

The agent explained:
> The agentic loop is the iterative cycle an AI agent follows to accomplish tasks.
> Instead of a simple request → response pattern, an agent repeatedly goes through
> these phases: Perceive → Think/Plan → Act → Observe → Repeat

The agent described how this enables autonomy — the agent can handle multi-step tasks,
recover from errors, and use tools without needing the user to guide every single step.

**Q2: "What labs are available in our LMS?"**

The agent could NOT return real backend data. It inspected local repo files 
(`lab/tasks/required/`) and listed the lab tasks from the repository structure.
This confirms the agent needs MCP tools (Task 1B) to access live LMS backend data.

## Task 1B — Agent with LMS tools

**Q1: "What labs are available?"**

The agent successfully called the MCP tool `mcp_lms_lms_labs` and returned real lab data from the backend:

> Here are the available labs:
> 1. Lab 01 – Products, Architecture & Roles
> 2. Lab 02 — Run, Fix, and Deploy a Backend Service
> 3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
> 4. Lab 04 — Testing, Front-end, and AI Agents
> 5. Lab 05 — Data Pipeline and Analytics Dashboard
> 6. Lab 06 — Build Your Own Agent
> 7. Lab 07 — Build a Client with an AI Coding Agent
> 8. Lab 08 — lab-08

**Q2: "Is the LMS backend healthy?"**

The agent called `mcp_lms_lms_health` and responded:

> Yes, the LMS backend is healthy! It currently has 56 items.

This confirms the MCP tools are working and the agent can query live backend data.

## Task 1C — Skill prompt

**Q: "Show me the scores" (without specifying a lab)**

The agent followed the skill prompt strategy:

1. First called `lms_labs` to get available labs
2. Listed all 8 labs
3. Asked: "Which lab would you like to see the scores for?"

Response:
> Here are the available labs:
> 1. Lab 01 – Products, Architecture & Roles
> 2. Lab 02 — Run, Fix, and Deploy a Backend Service
> ...
> 8. Lab 08 — lab-08
>
> Which lab would you like to see the scores for?

This shows the skill prompt is working — the agent now asks for clarification when a lab parameter is missing, instead of guessing or failing.

## Task 2A — Deployed agent

Nanobot gateway startup log excerpt:

```
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-03-31 01:01:23.829 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
2026-03-31 01:01:25.770 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_health' from server 'lms'
2026-03-31 01:01:25.771 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_labs' from server 'lms'
...
2026-03-31 01:01:26.526 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_webchat_ui_message' from server 'webchat'
2026-03-31 01:01:26.526 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

All services running:
- nanobot: Up with webchat channel and MCP tools (lms, webchat)
- backend: Up (healthy)
- qwen-code-api: Up (healthy)
- caddy: Up (gateway)

## Task 2B — Web client

Flutter web client accessible at `http://<vm-ip>:42002/flutter`

The web client connects to the nanobot agent via WebSocket at `/ws/chat`.
Login is protected by `NANOBOT_ACCESS_KEY`.

Tested endpoints:
- `curl http://localhost:42002/flutter` - Returns Flutter web app HTML
- WebSocket endpoint: `ws://localhost:42002/ws/chat?access_key=...`

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
