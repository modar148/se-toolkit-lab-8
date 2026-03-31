"""MCP server implementation for observability tools."""

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("mcp-obs")

# VictoriaLogs and VictoriaTraces URLs (container-local)
VICTORIALOGS_URL = "http://victorialogs:9428"
VICTORIATRACES_URL = "http://victoriatraces:10428"


class LogEntry(BaseModel):
    """A single log entry from VictoriaLogs."""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    level: str = Field(..., description="Log level (INFO, ERROR, etc.)")
    service: str = Field(..., description="Service name")
    event: str = Field(..., description="Event name")
    message: str = Field(..., description="Log message")
    trace_id: str | None = Field(None, description="Associated trace ID")


class TraceSummary(BaseModel):
    """Summary of a trace from VictoriaTraces."""

    trace_id: str = Field(..., description="Unique trace identifier")
    service: str = Field(..., description="Primary service name")
    duration_ms: int = Field(..., description="Total trace duration in milliseconds")
    span_count: int = Field(..., description="Number of spans in the trace")
    has_error: bool = Field(..., description="Whether the trace contains errors")


@mcp.tool()
async def logs_search(
    query: str = Field(..., description="LogsQL query string, e.g., 'service.name:\"LMS\" severity:ERROR'"),
    limit: int = Field(default=20, description="Maximum number of log entries to return"),
) -> list[dict]:
    """Search VictoriaLogs using LogsQL query.
    
    Useful fields to filter by:
    - service.name: e.g., "Learning Management Service"
    - severity: INFO, ERROR, WARNING, etc.
    - event: e.g., "db_query", "request_started"
    - trace_id: to find logs for a specific trace
    
    Time range can be specified with _time:1h, _time:10m, etc.
    
    Example queries:
    - '_time:1h service.name:"Learning Management Service" severity:ERROR'
    - '_time:10m event:db_query'
    - 'trace_id:a0c8b0e73b6380cac32d5e24821b9cd5'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{VICTORIALOGS_URL}/select/logsql/query"
        params = {"query": query, "limit": limit}
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json() if resp.content else []


@mcp.tool()
async def logs_error_count(
    service: str = Field(default="Learning Management Service", description="Service name to filter"),
    minutes: int = Field(default=60, description="Time window in minutes"),
) -> dict:
    """Count errors per service over a time window.
    
    Returns the count of ERROR-level log entries for the specified service.
    """
    query = f'_time:{minutes}m service.name:"{service}" severity:ERROR'
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{VICTORIALOGS_URL}/select/logsql/query"
        params = {"query": query, "limit": 1000}
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        logs = resp.json() if resp.content else []
        return {"service": service, "error_count": len(logs), "time_window_minutes": minutes, "logs": logs[:10]}


@mcp.tool()
async def traces_list(
    service: str = Field(default="Learning Management Service", description="Service name to filter"),
    limit: int = Field(default=10, description="Maximum number of traces to return"),
) -> list[TraceSummary]:
    """List recent traces for a service from VictoriaTraces.
    
    Returns a summary of recent traces including trace ID, duration, and error status.
    """
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
            
            # Check for errors in spans
            has_error = any(
                tag.get("key") == "error" or tag.get("key") == "error.message"
                for span in spans
                for tag in span.get("tags", [])
            )
            
            # Calculate duration
            duration_ms = 0
            for span in spans:
                if span.get("duration"):
                    span_duration = span["duration"] // 1000000  # Convert from microseconds
                    if span_duration > duration_ms:
                        duration_ms = span_duration
            
            results.append(
                TraceSummary(
                    trace_id=trace_id,
                    service=service,
                    duration_ms=duration_ms,
                    span_count=len(spans),
                    has_error=has_error,
                ).model_dump()
            )
        
        return results


@mcp.tool()
async def traces_get(
    trace_id: str = Field(..., description="The trace ID to fetch"),
) -> dict:
    """Fetch a specific trace by ID from VictoriaTraces.
    
    Returns the full trace with all spans, tags, and timing information.
    Useful for debugging a specific failed request.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        
        # Jaeger API returns {"data": [traces]}, we want the first trace
        traces = data.get("data", [])
        if not traces:
            return {"error": f"Trace {trace_id} not found"}
        
        trace = traces[0]
        
        # Summarize the trace
        spans = trace.get("spans", [])
        span_summary = []
        for span in spans:
            span_info = {
                "operation": span.get("operationName", "unknown"),
                "duration_ms": (span.get("duration", 0) or 0) // 1000000,
                "tags": {
                    tag.get("key"): str(tag.get("value", ""))
                    for tag in span.get("tags", [])
                    if tag.get("key") in ["http.method", "http.status_code", "error", "db.system"]
                },
            }
            span_summary.append(span_info)
        
        return {
            "trace_id": trace.get("traceID"),
            "span_count": len(spans),
            "spans": span_summary,
            "has_error": any(
                tag.get("key") == "error"
                for span in spans
                for tag in span.get("tags", [])
            ),
        }
