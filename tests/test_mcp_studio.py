"""
test_mcp_studio.py
==================
Unit and integration tests for MCP Server Developer Studio:
  - Tool and Resource JSON Schema generation
  - FastMCP Python code generation
  - Claude Desktop configuration snippet generation
  - JSON-RPC 2.0 sandbox tool execution
  - Default preset catalog validation
"""

import json
import pytest
from agent_core.mcp_studio import (
    MCPToolDefinition,
    MCPToolParameter,
    MCPResourceDefinition,
    MCPServerDefinition,
    MCPServerScaffolder,
    MCPSandboxTester,
    get_default_mcp_presets,
)


class TestMCPServerStudio:
    def test_mcp_tool_schema_generation(self):
        tool = MCPToolDefinition(
            name="multiply",
            description="Multiplies two numbers",
            parameters=[
                MCPToolParameter("a", "number", "First factor", required=True),
                MCPToolParameter("b", "number", "Second factor", required=True),
            ],
            handler_code="return json.dumps({'result': a * b})"
        )
        schema = tool.to_mcp_tool_schema()
        assert schema["name"] == "multiply"
        assert schema["description"] == "Multiplies two numbers"
        assert "inputSchema" in schema
        assert "a" in schema["inputSchema"]["properties"]
        assert "b" in schema["inputSchema"]["properties"]
        assert schema["inputSchema"]["required"] == ["a", "b"]

    def test_mcp_server_scaffolding_python(self):
        sdef = MCPServerDefinition(
            server_name="math-engine",
            description="Simple arithmetic MCP server",
            tools=[
                MCPToolDefinition(
                    name="add",
                    description="Adds two integers",
                    parameters=[
                        MCPToolParameter("x", "integer", "First addend"),
                        MCPToolParameter("y", "integer", "Second addend"),
                    ],
                    handler_code="return json.dumps({'sum': x + y})"
                )
            ]
        )
        code = MCPServerScaffolder.generate_python_server(sdef)
        assert "from mcp.server.fastmcp import FastMCP" in code
        assert 'FastMCP("math-engine")' in code
        assert "@mcp.tool()" in code
        assert "def add(x: int, y: int) -> str:" in code
        assert "transport=\"stdio\"" in code

    def test_mcp_claude_desktop_config(self):
        sdef = MCPServerDefinition(
            server_name="db-explorer",
            description="Database query server",
        )
        cfg_str = MCPServerScaffolder.generate_claude_desktop_config(sdef, script_path="C:/mcp/server.py")
        cfg = json.loads(cfg_str)
        assert "mcpServers" in cfg
        assert "db-explorer" in cfg["mcpServers"]
        assert cfg["mcpServers"]["db-explorer"]["command"] == "python"
        assert "C:/mcp/server.py" in cfg["mcpServers"]["db-explorer"]["args"]

    def test_mcp_sandbox_jsonrpc_execution(self):
        tester = MCPSandboxTester()
        tool = MCPToolDefinition(
            name="hash_text",
            description="Computes SHA-256",
            parameters=[MCPToolParameter("payload", "string", "Text to hash")],
            handler_code="import hashlib\nreturn hashlib.sha256(kwargs.get('payload', '').encode('utf-8')).hexdigest()"
        )
        res = tester.test_tool_execution(tool, {"payload": "antigravity"})
        assert res["status"] == "success"
        assert res["exit_code"] == 0
        assert "jsonrpc" in res
        assert res["jsonrpc"]["jsonrpc"] == "2.0"
        content = res["jsonrpc"]["result"]["content"]
        assert len(content) > 0
        # SHA-256 of 'antigravity'
        assert len(content[0]["text"]) == 64

    def test_default_mcp_presets(self):
        presets = get_default_mcp_presets()
        assert len(presets) >= 3
        names = [p.server_name for p in presets]
        assert "sqlite-query-engine" in names
        assert "weather-satellite-mcp" in names
        assert "crypto-hash-engine" in names
