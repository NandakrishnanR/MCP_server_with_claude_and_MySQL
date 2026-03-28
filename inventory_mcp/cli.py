"""CLI entry point for the inventory MCP server."""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import mcp

def main():
    """Run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
