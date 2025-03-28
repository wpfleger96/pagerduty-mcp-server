"""PagerDuty MCP Server

A server that exposes PagerDuty API functionality to LLMs. This server is designed to be used programmatically, with structured inputs and outputs.
"""

from .server import server
from .__main__ import main

__all__ = ['server', 'main']
