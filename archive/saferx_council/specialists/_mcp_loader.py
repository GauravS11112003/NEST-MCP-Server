"""
Helper to load Clinical Knowledge MCP tools into specialist agents.

Each specialist gets the subset of MCP tools relevant to its role.
The MCP server can run either in-process (stdio) or remote (SSE);
this loader picks the right transport based on env var.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# When True, specialist agents skip MCP loading and use bundled fallback tools.
# Useful in CI / when the MCP server isn't running.
SKIP_MCP = os.getenv("SAFERX_SKIP_MCP", "false").lower() == "true"


def get_mcp_toolset_or_none(tool_filter: list[str] | None = None):
    """Try to construct an ADK MCPToolset wired to clinical-knowledge-mcp.

    Returns None if MCP is disabled or import fails — callers should fall
    back to local Python tool functions in that case.
    """
    if SKIP_MCP:
        logger.info("SAFERX_SKIP_MCP=true — specialists will use bundled fallback tools")
        return None

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import (
            SseConnectionParams,
            StdioConnectionParams,
        )
    except Exception as e:
        logger.warning("MCPToolset import failed (%s) — falling back to local tools", e)
        return None

    mcp_url = os.getenv("CLINICAL_KNOWLEDGE_MCP_URL")
    try:
        if mcp_url:
            logger.info("Wiring specialists to MCP via SSE: %s", mcp_url)
            connection = SseConnectionParams(url=mcp_url)
        else:
            logger.info("Wiring specialists to MCP via stdio (in-process)")
            connection = StdioConnectionParams(
                server_params={
                    "command": "python",
                    "args": ["-m", "clinical_knowledge_mcp.server"],
                }
            )
        return MCPToolset(connection_params=connection, tool_filter=tool_filter)
    except Exception as e:
        logger.warning("MCPToolset construction failed (%s) — falling back to local tools", e)
        return None
