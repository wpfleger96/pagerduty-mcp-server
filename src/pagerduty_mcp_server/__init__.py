import asyncio
import argparse

from .server import server

def main():
    """PagerDuty MCP Server"""

    parser = argparse.ArgumentParser(description="PagerDuty MCP Server")
    parser.parse_args()
    server.run()

if __name__ == "__main__":
    main()
