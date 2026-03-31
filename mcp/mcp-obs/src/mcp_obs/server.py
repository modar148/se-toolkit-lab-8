"""MCP server implementation for observability tools."""

import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create server instance
server = Server("mcp-obs")

VICTORIALOGS_URL = "http://victorialogs:9428"
VICTORIATRACES_URL = "http://victoriatraces:10428"


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="logs_search",
            description="Search VictoriaLogs using LogsQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "LogsQL query string"},
                    "limit": {"type": "integer", "default": 20, "description": "Maximum number of log entries"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="logs_error_count",
            description="Count errors per service over a time window",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "default": "Learning Management Service"},
                    "minutes": {"type": "integer", "default": 60},
                },
            },
        ),
        Tool(
            name="traces_list",
            description="List recent traces for a service from VictoriaTraces",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "default": "Learning Management Service"},
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
        Tool(
            name="traces_get",
            description="Fetch a specific trace by ID from VictoriaTraces",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "The trace ID to fetch"},
                },
                "required": ["trace_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "logs_search":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{VICTORIALOGS_URL}/select/logsql/query"
                params = {"query": query, "limit": limit}
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                result = resp.json() if resp.content else []
            return [TextContent(type="text", text=str(result))]

        elif name == "logs_error_count":
            service = arguments.get("service", "Learning Management Service")
            minutes = arguments.get("minutes", 60)
            query = f'_time:{minutes}m service.name:"{service}" severity:ERROR'
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{VICTORIALOGS_URL}/select/logsql/query"
                params = {"query": query, "limit": 1000}
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                logs = resp.json() if resp.content else []
            return [TextContent(type="text", text=str({"service": service, "error_count": len(logs), "time_window_minutes": minutes, "logs": logs[:10]}))]

        elif name == "traces_list":
            service = arguments.get("service", "Learning Management Service")
            limit = arguments.get("limit", 10)
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces"
                params = {"service": service, "limit": limit}
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                results = []
                for trace_data in data.get("data", []):
                    trace_id = trace_data.get("traceID", "")
                    spans = trace_data.get("spans", [])
                    has_error = any(tag.get("key") == "error" for span in spans for tag in span.get("tags", []))
                    duration_ms = max((span.get("duration", 0) or 0) // 1000000 for span in spans) if spans else 0
                    results.append({"trace_id": trace_id, "service": service, "duration_ms": duration_ms, "span_count": len(spans), "has_error": has_error})
            return [TextContent(type="text", text=str(results))]

        elif name == "traces_get":
            trace_id = arguments.get("trace_id", "")
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                traces = data.get("data", [])
                if not traces:
                    return [TextContent(type="text", text=f"Trace {trace_id} not found")]
                trace = traces[0]
                spans = trace.get("spans", [])
                span_summary = [{"operation": span.get("operationName", "unknown"), "duration_ms": (span.get("duration", 0) or 0) // 1000000} for span in spans]
                result = {"trace_id": trace.get("traceID"), "span_count": len(spans), "spans": span_summary}
            return [TextContent(type="text", text=str(result))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
