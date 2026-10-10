"""MCP boundary tests: verify PagerDuty failures and current-user scope guards surface correctly through the tool interface."""

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.client import Client
from mcp.types import CallToolResult, ContentBlock, TextContent

from pagerduty_mcp_server.errors import PagerDutyAuthError
from pagerduty_mcp_server.server import mcp


def _text(content: list[ContentBlock]) -> str:
    return cast(TextContent, content[0]).text


def _user_context(
    *, team_ids: list[str], escalation_policy_ids: list[str]
) -> dict[str, Any]:
    """Build a current-user context with the given teams and escalation policies."""
    return {
        "user_id": "PUSER1",
        "name": "Test User",
        "email": "user@example.com",
        "team_ids": team_ids,
        "service_ids": [],
        "escalation_policy_ids": escalation_policy_ids,
    }


async def _call_tool_as(
    user_context: dict[str, Any],
    tool_name: str,
    list_module: str,
    args: dict[str, Any],
) -> tuple[CallToolResult, AsyncMock]:
    """Call a tool as the given current user; return (result, paginate mock)."""
    mocked_paginate = AsyncMock(return_value=[])

    with (
        patch(
            "pagerduty_mcp_server.server.users.build_user_context",
            AsyncMock(return_value=user_context),
        ),
        patch(f"{list_module}.create_client", MagicMock()),
        patch(f"{list_module}.paginate", mocked_paginate),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool_mcp(tool_name, args)

    return result, mocked_paginate


def _paginate_params(mocked_paginate: AsyncMock) -> dict[str, Any]:
    """Return the query params of the single awaited paginate call."""
    mocked_paginate.assert_awaited_once()
    assert mocked_paginate.await_args is not None
    params: dict[str, Any] = mocked_paginate.await_args.kwargs["params"]
    return params


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


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
@pytest.mark.parametrize(
    ("tool_name", "list_module"),
    [
        ("get_incidents", "pagerduty_mcp_server.incidents"),
        ("get_services", "pagerduty_mcp_server.services"),
        ("get_users", "pagerduty_mcp_server.users"),
    ],
)
async def test_current_user_without_teams_rejects_unscoped_query(
    tool_name: str, list_module: str
) -> None:
    """A user with no teams must get an error, not an unfiltered account-wide query."""
    result, mocked_paginate = await _call_tool_as(
        _user_context(team_ids=[], escalation_policy_ids=[]), tool_name, list_module, {}
    )

    assert result.isError is True
    assert result.content
    assert "not a member of any PagerDuty team" in _text(result.content)
    mocked_paginate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
@pytest.mark.parametrize(
    ("tool_name", "list_module", "args"),
    [
        pytest.param(
            "get_incidents",
            "pagerduty_mcp_server.incidents",
            {"team_ids": [""]},
            id="incidents-blank-team",
        ),
        pytest.param(
            "get_incidents",
            "pagerduty_mcp_server.incidents",
            {"service_ids": [" "]},
            id="incidents-blank-service",
        ),
        pytest.param(
            "get_services",
            "pagerduty_mcp_server.services",
            {"team_ids": [""]},
            id="services-blank-team",
        ),
        pytest.param(
            "get_users",
            "pagerduty_mcp_server.users",
            {"team_ids": ["  "]},
            id="users-blank-team",
        ),
        pytest.param(
            "get_escalation_policies",
            "pagerduty_mcp_server.escalation_policies",
            {"user_ids": [""]},
            id="escalation-policies-blank-user",
        ),
        pytest.param(
            "get_escalation_policies",
            "pagerduty_mcp_server.escalation_policies",
            {"team_ids": [" "]},
            id="escalation-policies-blank-team",
        ),
    ],
)
async def test_blank_filter_ids_reject_unscoped_query(
    tool_name: str, list_module: str, args: dict[str, Any]
) -> None:
    """Blank IDs must not count as a filter when current_user_context is False."""
    result, mocked_paginate = await _call_tool_as(
        _user_context(team_ids=["T1"], escalation_policy_ids=[]),
        tool_name,
        list_module,
        {"current_user_context": False, **args},
    )

    assert result.isError is True
    assert result.content
    assert "Must specify at least" in _text(result.content)
    mocked_paginate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_blank_filter_ids_dropped_from_mixed_list() -> None:
    """Blank IDs are dropped while real IDs in the same list are kept."""
    result, mocked_paginate = await _call_tool_as(
        _user_context(team_ids=["T1"], escalation_policy_ids=[]),
        "get_users",
        "pagerduty_mcp_server.users",
        {"current_user_context": False, "team_ids": ["", "T1"]},
    )

    assert result.isError is False
    assert _paginate_params(mocked_paginate)["team_ids[]"] == ["T1"]


_ONCALLS_MODULE = "pagerduty_mcp_server.oncalls"
_NO_POLICY_USER = _user_context(team_ids=["T1"], escalation_policy_ids=[])
_POLICY_USER = _user_context(team_ids=["T1"], escalation_policy_ids=["EP1", "EP2"])


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_get_oncalls_without_policies_rejects_unscoped_query() -> None:
    """A user on no escalation policy must get an error, not account-wide on-calls."""
    result, mocked_paginate = await _call_tool_as(
        _NO_POLICY_USER, "get_oncalls", _ONCALLS_MODULE, {}
    )

    assert result.isError is True
    assert "not a target of any PagerDuty escalation policy" in _text(result.content)
    mocked_paginate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_get_oncalls_without_policies_allows_schedule_ids() -> None:
    """schedule_ids alone still scopes the query when the user has no policies."""
    result, mocked_paginate = await _call_tool_as(
        _NO_POLICY_USER, "get_oncalls", _ONCALLS_MODULE, {"schedule_ids": ["SCHED1"]}
    )

    assert result.isError is False
    params = _paginate_params(mocked_paginate)
    assert params["schedule_ids[]"] == ["SCHED1"]
    assert "escalation_policy_ids[]" not in params


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_get_oncalls_without_policies_rejects_blank_schedule_ids() -> None:
    """Blank schedule IDs must not count as a scope filter."""
    result, mocked_paginate = await _call_tool_as(
        _NO_POLICY_USER, "get_oncalls", _ONCALLS_MODULE, {"schedule_ids": [""]}
    )

    assert result.isError is True
    assert "not a target of any PagerDuty escalation policy" in _text(result.content)
    mocked_paginate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_get_oncalls_uses_current_user_policies() -> None:
    """By default, on-calls are filtered to the current user's escalation policies."""
    result, mocked_paginate = await _call_tool_as(
        _POLICY_USER, "get_oncalls", _ONCALLS_MODULE, {}
    )

    assert result.isError is False
    params = _paginate_params(mocked_paginate)
    assert params["escalation_policy_ids[]"] == ["EP1", "EP2"]


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.server
async def test_get_oncalls_rejects_policy_ids_with_user_context() -> None:
    """Caller-supplied escalation_policy_ids must not be silently overwritten."""
    result, mocked_paginate = await _call_tool_as(
        _POLICY_USER, "get_oncalls", _ONCALLS_MODULE, {"escalation_policy_ids": ["P1"]}
    )

    assert result.isError is True
    assert "escalation_policy_ids" in _text(result.content)
    mocked_paginate.assert_not_awaited()
