"""PagerDuty MCP error types."""

from fastmcp.exceptions import ToolError


class PagerDutyError(ToolError):
    """Base error for PagerDuty MCP failures."""


class PagerDutyAuthError(PagerDutyError):
    """Raised when PagerDuty credentials are missing or invalid."""


class PagerDutyResponseLimitError(PagerDutyError):
    """Raised when a response is too large to return safely."""
