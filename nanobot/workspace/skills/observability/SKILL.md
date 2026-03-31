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

### When the user asks about errors or failures:

1. First call `logs_error_count` for the LMS backend service to see if there are recent errors
2. If errors exist, call `logs_search` with a query like:
   - `_time:10m service.name:"Learning Management Service" severity:ERROR`
3. Look for a `trace_id` in the error logs
4. If you find a trace_id, call `traces_get` to inspect the full trace
5. Summarize what went wrong — don't dump raw JSON

### When the user asks about system health:

1. Check `logs_error_count` for the last 10 minutes
2. If no errors, report the system is healthy
3. If errors exist, investigate with `logs_search` and `traces_get`

### Useful LogsQL queries:

- `_time:10m service.name:"Learning Management Service" severity:ERROR` — Recent LMS errors
- `_time:1h event:db_query severity:ERROR` — Database errors in the last hour
- `trace_id:<id>` — All logs for a specific trace

### Response format:

- Keep responses concise
- Summarize findings, don't dump raw JSON
- If you find an error, explain:
  - What service failed
  - What the error was
  - When it happened
  - The trace ID if available
