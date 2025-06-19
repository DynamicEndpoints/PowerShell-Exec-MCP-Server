"""Main entry point for MCP PowerShell server."""
from .server import mcp

def main():
    """Run the MCP PowerShell server."""
    mcp.run()

if __name__ == '__main__':
    main()
