"""PagerDuty MCP Server

A server that exposes PagerDuty API functionality to LLMs. This server is designed to be used programmatically, with structured inputs and outputs.
"""

from .server import mcp

__all__ = ["main", "mcp"]


def main():
    """Entry point for the PagerDuty MCP Server."""
    from .__main__ import main as _main

    return _main()
