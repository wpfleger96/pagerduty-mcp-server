"""Main entry point for the PagerDuty MCP Server."""

import argparse
import logging
import sys
from importlib.metadata import version

from .server import mcp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pagerduty_mcp_server")


def main():
    """PagerDuty MCP Server entry point."""
    parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
    parser.parse_args()

    logger.info(f"Starting PagerDuty MCP Server v{version('pagerduty_mcp_server')}...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
