"""MCP Client for connecting to the company's MCP server via HTTP."""

import json
import logging
import uuid
from typing import Any

import httpx

from config import MCP_SERVER_URL

logger = logging.getLogger(__name__)


class MCPHttpClient:
    """HTTP-based MCP client for Streamable HTTP transport."""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id: str | None = None
        self._tools: list[dict] | None = None

    async def initialize(self) -> dict:
        """Initialize the MCP session."""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "customer-support-chatbot",
                    "version": "1.0.0"
                }
            }
        }

        result = await self._send_request(request)
        logger.info(f"MCP session initialized: {result}")
        return result

    async def list_tools(self) -> list[dict]:
        """List all available tools from the MCP server."""
        if self._tools is not None:
            return self._tools

        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }

        result = await self._send_request(request)
        tools = result.get("tools", [])

        self._tools = [
            {
                "name": tool["name"],
                "description": tool.get("description", f"Execute {tool['name']}"),
                "input_schema": tool.get("inputSchema", {"type": "object", "properties": {}}),
            }
            for tool in tools
        ]

        logger.info(f"Listed {len(self._tools)} tools from MCP server")
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool on the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }

        logger.info(f"Calling tool: {name} with args: {arguments}")
        result = await self._send_request(request)

        # Extract text content from result
        content = result.get("content", [])
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            return "\n".join(text_parts) if text_parts else json.dumps(result)

        return str(content)

    async def _send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        try:
            response = await self.client.post(
                self.server_url,
                json=request,
                headers=headers
            )

            # Capture session ID from response headers
            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]

            # Handle SSE response
            content_type = response.headers.get("content-type", "")

            if "text/event-stream" in content_type:
                # Parse SSE response
                return await self._parse_sse_response(response.text)

            # Handle regular JSON response
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Exception(f"MCP Error: {data['error']}")

            return data.get("result", data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with MCP server: {e}")
            raise

    async def _parse_sse_response(self, text: str) -> dict:
        """Parse Server-Sent Events response."""
        result = {}
        for line in text.split("\n"):
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str:
                    try:
                        data = json.loads(data_str)
                        if "result" in data:
                            result = data["result"]
                        elif "error" in data:
                            raise Exception(f"MCP Error: {data['error']}")
                    except json.JSONDecodeError:
                        continue
        return result

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_mcp_client: MCPHttpClient | None = None


async def get_mcp_client() -> MCPHttpClient:
    """Get or create the MCP client."""
    global _mcp_client

    if _mcp_client is None:
        _mcp_client = MCPHttpClient(MCP_SERVER_URL)
        await _mcp_client.initialize()

    return _mcp_client


async def close_mcp_client():
    """Close the MCP client."""
    global _mcp_client

    if _mcp_client is not None:
        await _mcp_client.close()
        _mcp_client = None


async def list_tools() -> list[dict[str, Any]]:
    """List all available tools from the MCP server."""
    client = await get_mcp_client()
    return await client.list_tools()


async def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool on the MCP server."""
    client = await get_mcp_client()
    return await client.call_tool(name, arguments)


def convert_tools_to_openai_format(mcp_tools: list[dict]) -> list[dict]:
    """Convert MCP tools to OpenAI function calling format."""
    openai_tools = []

    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            }
        })

    return openai_tools
