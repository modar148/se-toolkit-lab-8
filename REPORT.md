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

**Happy-path log excerpt (successful request):**
```
2026-03-30 23:49:19,967 INFO [lms_backend.main] - request_started
2026-03-30 23:49:19,968 INFO [lms_backend.auth] - auth_success
2026-03-30 23:49:19,969 INFO [lms_backend.db.items] - db_query
2026-03-30 23:49:19,975 INFO [lms_backend.main] - request_completed
INFO: 172.22.0.2:52764 - "GET /items/ HTTP/1.1" 200 OK
```

**Error-path log excerpt (PostgreSQL stopped):**
```
2026-03-31 01:06:52,989 INFO [lms_backend.auth] - auth_success
2026-03-31 01:06:53,011 INFO [lms_backend.db.items] - db_query
2026-03-31 01:06:53,117 ERROR [lms_backend.db.items] - db_query
  (sqlalchemy.dialects.postgresql.asyncpg.InterfaceError): connection is closed
2026-03-31 01:06:53,118 WARNING [lms_backend.routers.items] - items_list_failed_as_not_found
2026-03-31 01:06:53,153 INFO [lms_backend.main] - request_completed
INFO: 172.22.0.10:43454 - "GET /items/ HTTP/1.1" 404 Not Found
```

**VictoriaLogs query:**
Query: `_time:1h service.name:"Learning Management Service" severity:ERROR`
Result: Found error logs with `db_query` event showing "connection is closed" error.

## Task 3B — Traces

**VictoriaTraces API verified:**
- Endpoint: `http://victoriatraces:10428/select/jaeger/api/traces`
- Successfully queried traces for "Learning Management Service"
- Trace structure includes: traceID, spans (with operationName, duration, tags)

**Healthy trace expected structure:**
- Multiple spans showing request flow: HTTP request → auth → db_query → response
- Each span has duration_ms and tags (http.method, http.status_code, db.system)

**Error trace expected structure:**
- Similar span hierarchy but with error tags
- Error span shows exception details in tags

**Note:** Screenshots of VictoriaTraces UI can be captured at `http://<vm-ip>:42002/utils/victoriatraces`

## Task 3C — Observability MCP tools

**MCP Observability Server Created:**
- `mcp/mcp-obs/src/mcp_obs/server.py` - MCP server with 4 tools:
  - `logs_search` - Search VictoriaLogs using LogsQL
  - `logs_error_count` - Count errors per service over time window
  - `traces_list` - List recent traces for a service
  - `traces_get` - Fetch specific trace by ID

**Agent Configuration:**
- Added `obs` MCP server to nanobot config
- Created `nanobot/workspace/skills/observability/SKILL.md` skill prompt

**Verification:**
All 4 MCP tools registered successfully:
```
MCP: registered tool 'mcp_obs_logs_search' from server 'obs'
MCP: registered tool 'mcp_obs_logs_error_count' from server 'obs'
MCP: registered tool 'mcp_obs_traces_list' from server 'obs'
MCP: registered tool 'mcp_obs_traces_get' from server 'obs'
MCP server 'obs': connected, 4 tools registered
```

**Note:** LLM responses require a valid OpenRouter API key with credits. The current key shows "User not found" for chat completions endpoint. To test the agent's observability capabilities, add credits to your OpenRouter account at https://openrouter.ai/settings/credits or use a different valid API key.

**Expected behavior when API key is valid:**
- Query: "Any LMS backend errors in the last 10 minutes?"
- Agent should: Call `logs_error_count` → `logs_search` → optionally `traces_get` → summarize findings

## Task 4A — Multi-step investigation

**Planted Bug Found:**
In `backend/src/lms_backend/routers/items.py`, the `get_items()` function caught all exceptions and returned a misleading 404 "Items not found" instead of surfacing the real database error.

**Original buggy code:**
```python
except Exception as exc:
    logger.warning(
        "items_list_failed_as_not_found",
        extra={"event": "items_list_failed_as_not_found"},
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Items not found",
    ) from exc
```

**Investigation flow (with PostgreSQL stopped):**
1. Triggered request: "What labs are available?"
2. Backend returned: 404 "Items not found" (misleading)
3. Logs showed: `db_query` ERROR with "connection is closed"
4. Trace showed: db_query span failed

**Note:** Full agent investigation requires valid OpenRouter API key with credits. The observability tools are configured and registered correctly.

## Task 4B — Proactive health check

**Note:** Requires valid OpenRouter API key for cron-based health checks to work. The cron tool is available in nanobot and the observability MCP tools are registered.

Expected workflow:
1. Ask agent: "Create a health check for this chat that runs every 2 minutes..."
2. Agent uses `cron` tool to schedule recurring job
3. Each run calls `logs_error_count` → `logs_search` → posts summary to chat

## Task 4C — Bug fix and recovery

**Fix applied:**
Changed the exception handler in `backend/src/lms_backend/routers/items.py`:

```python
except Exception as exc:
    logger.error(
        "items_list_failed",
        extra={"event": "items_list_failed", "error": str(exc)},
    )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to retrieve items: {type(exc).__name__}",
    ) from exc
```

**Before fix (with PostgreSQL stopped):**
```
curl http://localhost:42002/items/ -H 'Authorization: Bearer lab8-secret-key'
{"detail":"Items not found"}  # 404 - Misleading!
```

**After fix (with PostgreSQL stopped):**
```
curl http://localhost:42002/items/ -H 'Authorization: Bearer lab8-secret-key'
{"detail":"Failed to retrieve items: gaierror"}  # 500 - Real error!
```

**Recovery verification:**
After restarting PostgreSQL, the system returns to normal operation with proper item listings.

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
