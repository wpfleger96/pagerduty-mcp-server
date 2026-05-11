"""MCP boundary tests: verify PagerDuty failures set isError=true."""

from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.client import Client
from mcp.types import TextContent

from pagerduty_mcp_server.errors import PagerDutyAuthError
from pagerduty_mcp_server.server import mcp


def _text(content: list) -> str:  # type: ignore[type-arg]
    return cast(TextContent, content[0]).text


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_auth_error_sets_is_error() -> None:
    """Auth failures should surface as MCP tool errors."""
    with patch(
        "pagerduty_mcp_server.server.teams.create_client",
        side_effect=PagerDutyAuthError(
            "PagerDuty credentials are not configured for this request."
        ),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool_mcp("get_teams", {"limit": 1})

    assert result.isError is True
    assert result.content
    assert "PagerDuty credentials are not configured for this request." in _text(
        result.content
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_validation_error_sets_is_error() -> None:
    """Validation failures should surface as MCP tool errors."""
    async with Client(mcp) as client:
        result = await client.call_tool_mcp(
            "get_teams", {"team_id": "TEAM123", "limit": 1}
        )

    assert result.isError is True
    assert result.content
    assert "When `team_id` is provided" in _text(result.content)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_successful_call_sets_is_error_false() -> None:
    """Successful tool calls should not set isError."""
    mocked_list_teams = AsyncMock(
        return_value={
            "metadata": {
                "count": 1,
                "description": "Found 1 result for resource type teams",
            },
            "teams": [{"id": "team-1", "name": "Engineering"}],
        }
    )

    with patch("pagerduty_mcp_server.server.teams.list_teams", mocked_list_teams):
        async with Client(mcp) as client:
            result = await client.call_tool_mcp("get_teams", {"limit": 1})

    assert result.isError is False
