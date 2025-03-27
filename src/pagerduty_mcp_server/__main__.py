"""Main entry point for the PagerDuty MCP Server."""

import os
import sys
import signal
import argparse
import logging
import logging.handlers
import atexit

from .client import get_api_client
from .server import server

os.makedirs('./log', exist_ok=True)

file_handler = logging.handlers.RotatingFileHandler(
    filename='./log/pagerduty-mcp-server.log',
    maxBytes=1024*1024,  # 1MB
    backupCount=50
)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully.
    
    This function is called when the server receives a shutdown signal (SIGINT or SIGTERM).
    It logs the shutdown message and ensures clean exit.
    
    Args:
        signum (int): The signal number
        frame (frame): The current stack frame
    """
    logger.info("Received shutdown signal, stopping server...")
    try:
        server.stop()
    except Exception as e:
        logger.error(f"Error during server shutdown: {e}")
    finally:
        sys.exit(0)

def main():
    """PagerDuty MCP Server entry point.
    
    This function initializes the server, sets up signal handlers, and starts the server.
    It handles various error conditions and ensures proper cleanup.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
    parser.parse_args()

    try:
        get_api_client()
    except SystemExit:
        return 1

    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Register cleanup function
    atexit.register(handle_shutdown, None, None)

    logger.info("Starting PagerDuty MCP Server...")
    try:
        server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
