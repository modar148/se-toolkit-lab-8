#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then execs into 'nanobot gateway'.
"""

import json
import os
import sys
from pathlib import Path


def main():
    config_path = Path("/app/nanobot/config.json")
    workspace_path = Path(os.environ.get("NANOBOT_WORKSPACE", "/app/nanobot/workspace"))
    resolved_path = Path("/app/nanobot/config.resolved.json")

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override from environment variables
    # LLM provider settings
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base = os.environ.get("LLM_API_BASE_URL")
    llm_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        if "openrouter" in config.get("providers", {}):
            config["providers"]["openrouter"]["apiKey"] = llm_api_key
        elif "custom" in config.get("providers", {}):
            config["providers"]["custom"]["apiKey"] = llm_api_key

    if llm_api_base:
        if "openrouter" in config.get("providers", {}):
            config["providers"]["openrouter"]["apiBase"] = llm_api_base
        elif "custom" in config.get("providers", {}):
            config["providers"]["custom"]["apiBase"] = llm_api_base

    if llm_model:
        config["agents"]["defaults"]["model"] = llm_model

    # Gateway settings
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config.setdefault("gateway", {})["host"] = gateway_host
    if gateway_port:
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # Webchat channel settings
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")

    if webchat_host or webchat_port:
        config.setdefault("channels", {}).setdefault("webchat", {})["enabled"] = True
        if webchat_host:
            config["channels"]["webchat"]["host"] = webchat_host
        if webchat_port:
            config["channels"]["webchat"]["port"] = int(webchat_port)
        if nanobot_access_key:
            config["channels"]["webchat"]["accessKey"] = nanobot_access_key

    # MCP webchat server settings
    mcp_webchat_url = os.environ.get("NANOBOT_MCP_WEBSOCKET_URL")
    mcp_webchat_token = os.environ.get("NANOBOT_MCP_WEBSOCKET_TOKEN")

    if mcp_webchat_url or mcp_webchat_token:
        config.setdefault("tools", {}).setdefault("mcpServers", {})["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
        }
        env = {}
        if mcp_webchat_url:
            env["NANOBOT_MCP_WEBSOCKET_URL"] = mcp_webchat_url
        if mcp_webchat_token:
            env["NANOBOT_MCP_WEBSOCKET_TOKEN"] = mcp_webchat_token
        if env:
            config["tools"]["mcpServers"]["webchat"]["env"] = env

    # LMS MCP server env vars (may need container-local URLs)
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if lms_backend_url or lms_api_key:
        if "lms" not in config.get("tools", {}).get("mcpServers", {}):
            config.setdefault("tools", {}).setdefault("mcpServers", {})["lms"] = {
                "command": "python",
                "args": ["-m", "mcp_lms"],
            }
        lms_env = config["tools"]["mcpServers"]["lms"].setdefault("env", {})
        if lms_backend_url:
            lms_env["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
        if lms_api_key:
            lms_env["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Observability MCP server (VictoriaLogs + VictoriaTraces)
    # Always register it if the config has it defined
    if "obs" in config.get("tools", {}).get("mcpServers", {}):
        # Keep the obs server configuration from config.json
        pass

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}")
    sys.stdout.flush()

    # Exec into nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_path),
        ],
    )


if __name__ == "__main__":
    main()
