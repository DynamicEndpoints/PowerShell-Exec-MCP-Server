#!/usr/bin/env python3
"""Startup script for PowerShell MCP server."""
import sys
import subprocess
import pkg_resources

def ensure_package(package_name):
    """Ensure a Python package is installed."""
    try:
        pkg_resources.require(package_name)
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Ensure required packages are installed
ensure_package("modelcontextprotocol")

import asyncio
from modelcontextprotocol.server import Server
from modelcontextprotocol.server.stdio import StdioServerTransport
from modelcontextprotocol.types import (
    CallToolRequestSchema,
    ListToolsRequestSchema,
    ErrorCode,
    McpError,
)

def create_server() -> Server:
    """Create and configure the MCP server instance."""
    server = Server(
        {
            "name": "powershell-integration",
            "version": "0.1.0"
        },
        {
            "capabilities": {
                "tools": True
            }
        }
    )

    # Set up error handling
    server.onerror = lambda error: print(f"[MCP Error] {str(error)}", file=sys.stderr)

    # Register tool list handler
    @server.setRequestHandler(ListToolsRequestSchema)
    async def handle_list_tools():
        return {
            "tools": [
                {
                    "name": "run_powershell",
                    "description": "Execute PowerShell commands securely",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "PowerShell code to execute"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Command timeout in seconds",
                                "minimum": 1,
                                "maximum": 300,
                                "default": 60
                            }
                        },
                        "required": ["code"]
                    }
                }
            ]
        }

    # Register tool call handler
    @server.setRequestHandler(CallToolRequestSchema)
    async def handle_tool_call(request):
        if request.params.name != "run_powershell":
            raise McpError(
                ErrorCode.MethodNotFound,
                f"Unknown tool: {request.params.name}"
            )

        code = request.params.arguments.get("code")
        if not isinstance(code, str):
            raise McpError(
                ErrorCode.InvalidParams,
                "code parameter must be a string"
            )

        timeout = request.params.arguments.get("timeout", 60)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            raise McpError(
                ErrorCode.InvalidParams,
                "timeout must be between 1 and 300 seconds"
            )

        try:
            process = await asyncio.create_subprocess_exec(
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                code,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            if process.returncode != 0:
                raise McpError(
                    ErrorCode.InternalError,
                    stderr or "Command failed with no error output"
                )

            return {
                "content": [
                    {
                        "type": "text",
                        "text": stdout
                    }
                ]
            }

        except asyncio.TimeoutError:
            process.kill()
            raise McpError(
                ErrorCode.Timeout,
                f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            raise McpError(
                ErrorCode.InternalError,
                str(e)
            )

    return server

async def run():
    """Run the MCP server."""
    server = create_server()
    transport = StdioServerTransport()
    await server.connect(transport)
    print("PowerShell MCP server running on stdio", file=sys.stderr)
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
