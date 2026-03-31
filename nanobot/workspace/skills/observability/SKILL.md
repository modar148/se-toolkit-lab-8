---
name: observability
description: Use observability MCP tools for logs and traces
always: true
---

# Observability Skill

You have access to observability MCP tools that can query VictoriaLogs and VictoriaTraces.

## Available Tools

**Log tools (VictoriaLogs):**
- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors for a service over a time window

**Trace tools (VictoriaTraces):**
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID

## Strategy Rules

### When the user asks "What went wrong?" or "Check system health":

Follow this investigation flow:

1. **Check for recent errors**: Call `logs_error_count` with `minutes=10` for "Learning Management Service"

2. **If errors exist, search logs**: Call `logs_search` with:
   - `_time:10m service.name:"Learning Management Service" severity:ERROR`

3. **Extract trace_id**: Look through the error logs for a `trace_id` field

4. **Fetch the trace**: Call `traces_get` with the trace_id to see the full request flow

5. **Summarize findings**: Provide a concise explanation that includes:
   - What service failed (e.g., "LMS backend")
   - What the error was (e.g., "PostgreSQL connection closed")
   - When it happened (timestamp from logs)
   - Evidence from both logs AND traces
   - The root failing operation (e.g., "db_query span failed")

### When the user asks about general system health:

1. Check `logs_error_count` for the last 10 minutes
2. If no errors, report the system is healthy
3. If errors exist, investigate with `logs_search` and `traces_get`

### Useful LogsQL queries:

- `_time:10m service.name:"Learning Management Service" severity:ERROR` — Recent LMS errors
- `_time:10m event:db_query severity:ERROR` — Database errors in the last 10 minutes
- `trace_id:<id>` — All logs for a specific trace

### Response format:

- Keep responses concise (2-4 sentences)
- Summarize findings, don't dump raw JSON
- Explicitly mention both log evidence AND trace evidence
- Name the affected service and the root failing operation
