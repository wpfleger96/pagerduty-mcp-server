import sys
import signal
import argparse
import logging

from .client import get_api_client
from .server import server, logger

def main():
    """PagerDuty MCP Server"""

    parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
    parser.parse_args()

    try:
        get_api_client()
    except SystemExit:
        return 1

    def handle_shutdown(signum, frame):
        logger.info("Received shutdown signal, stopping server...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)


    logger.info("Starting PagerDuty MCP Server...")
    try:
        server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
