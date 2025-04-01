"""Main entry point for the PagerDuty MCP Server."""

import sys
import argparse
import logging

from .client import get_api_client
from .server import server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pagerduty_mcp_server")

def main():
    """PagerDuty MCP Server entry point."""
    parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
    parser.parse_args()

    try:
        get_api_client()
    except SystemExit:
        return 1

    logger.info("Starting PagerDuty MCP Server...")
    try:
        server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
