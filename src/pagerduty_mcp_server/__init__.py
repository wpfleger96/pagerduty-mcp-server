"""PagerDuty MCP Server

A server that exposes PagerDuty API functionality to LLMs. This server is designed to be used programmatically, with structured inputs and outputs.
"""
import logging
from .client import get_api_client
from .server import mcp

__all__ = ["main", "mcp"]

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
logger = logging.getLogger("pagerduty_mcp_server")


def main():
    """Main entry point for the package."""
    try:        
        get_api_client()
    except SystemExit:
        return 1
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()