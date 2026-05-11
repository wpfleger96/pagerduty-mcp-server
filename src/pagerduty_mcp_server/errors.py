"""PagerDuty MCP error types."""

from fastmcp.exceptions import ToolError


class PagerDutyError(ToolError):
    """Base error for PagerDuty MCP failures."""


class PagerDutyAuthError(PagerDutyError):
    """Raised when PagerDuty credentials are missing or invalid."""
