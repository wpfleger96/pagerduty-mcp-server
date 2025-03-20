"""PagerDuty MCP Server package."""

import asyncio
import argparse
import logging

from .server import server

logger = logging.getLogger(__name__)

def main():
    """Start the PagerDuty MCP Server.
    
    This function initializes and starts the MCP server, which provides a REST API
    for interacting with PagerDuty resources. It sets up command line argument parsing
    and starts the server.
    
    Returns:
        None
        
    Raises:
        SystemExit: If the server fails to start or encounters a fatal error
    """
    try:
        parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
        parser.parse_args()
        server.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise SystemExit(1) from e

if __name__ == "__main__":
    main()
