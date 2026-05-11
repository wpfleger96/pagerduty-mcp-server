"""Unit tests for the users module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pagerduty_mcp_server import users, utils
from tests.helpers import ApiRuntimeError


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_list_users(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that users are fetched correctly."""
    mock_get_api_client.iter_all.return_value = mock_users

    user_list = await users.list_users()

    mock_get_api_client.iter_all.assert_called_once_with(
        users.USERS_URL, params={}, page_size=100
    )
    assert user_list == utils.api_response_handler(
        results=mock_users_parsed, resource_name="users"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_list_users_with_query(
    mock_get_api_client, mock_users, mock_users_parsed
):
    """Test that users can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.iter_all.return_value = mock_users

    user_list = await users.list_users(query=query)

    mock_get_api_client.iter_all.assert_called_once_with(
        users.USERS_URL, params={"query": query}, page_size=100
    )
    assert user_list == utils.api_response_handler(
        results=mock_users_parsed, resource_name="users"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_list_users_api_error(mock_get_api_client):
    """Test that list_users handles API errors correctly."""
    mock_get_api_client.iter_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await users.list_users()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_list_users_empty_response(mock_get_api_client):
    """Test that list_users handles empty response correctly."""
    mock_get_api_client.iter_all.return_value = []

    user_list = await users.list_users()
    assert user_list == utils.api_response_handler(results=[], resource_name="users")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_user(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that a single user is fetched correctly."""
    user_id = mock_users[0]["id"]
    mock_get_api_client.jget.return_value = {"user": mock_users[0]}

    user = await users.show_user(user_id=user_id)

    mock_get_api_client.jget.assert_called_once_with(f"{users.USERS_URL}/{user_id}")
    assert user == utils.api_response_handler(
        results=mock_users_parsed[0], resource_name="user"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_user_invalid_id(mock_get_api_client):
    """Test that show_user raises ValueError for invalid user ID."""
    with pytest.raises(ValueError) as exc_info:
        await users.show_user(user_id=None)
    assert str(exc_info.value) == "User ID is required"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_user_api_error(mock_get_api_client):
    """Test that show_user handles API errors correctly."""
    user_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await users.show_user(user_id=user_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_user_invalid_response(mock_get_api_client):
    """Test that show_user handles invalid API response correctly."""
    user_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'user' key

    with pytest.raises(RuntimeError) as exc_info:
        await users.show_user(user_id=user_id)
    assert (
        str(exc_info.value) == "Failed to fetch user 123: Response missing 'user' field"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.services.fetch_service_ids", new_callable=AsyncMock)
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_show_current_user,
    mock_user,
    mock_user_parsed,
    mock_team_ids,
    mock_service_ids,
    mock_escalation_policy_ids,
):
    """Test that the user context is built correctly with all data present."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_service_ids.return_value = mock_service_ids
    mock_fetch_escalation_policy_ids.return_value = mock_escalation_policy_ids
    user_context = await users.build_user_context()

    assert user_context["user_id"] == mock_user_parsed["id"]
    assert user_context["name"] == mock_user_parsed.get("name", "")
    assert user_context["email"] == mock_user_parsed.get("email", "")
    assert user_context["service_ids"] == mock_service_ids
    assert user_context["escalation_policy_ids"] == mock_escalation_policy_ids


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
async def test_build_user_context_missing_data(mock_show_current_user):
    """Test that build_user_context raises ValueError for missing data."""
    mock_show_current_user.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await users.build_user_context()
    assert str(exc_info.value) == "Failed to get current user data"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
async def test_build_user_context_error_handling(mock_show_current_user):
    """Test that build_user_context raises RuntimeError for API errors."""
    error = RuntimeError("API Error")
    mock_show_current_user.side_effect = error

    with pytest.raises(RuntimeError) as exc_info:
        await users.build_user_context()
    assert exc_info.value == error


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
async def test_build_user_context_none_user(mock_show_current_user):
    """Test that build_user_context raises ValueError for None user data."""
    mock_show_current_user.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await users.build_user_context()
    assert str(exc_info.value) == "Failed to get current user data"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_empty_teams(
    mock_fetch_escalation_policy_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context handles empty team data correctly."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_team_ids.return_value = []
    mock_fetch_escalation_policy_ids.return_value = []

    context = await users.build_user_context()
    assert context == {
        "user_id": str(mock_user_parsed["id"]),
        "name": mock_user_parsed.get("name", ""),
        "email": mock_user_parsed.get("email", ""),
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": [],
    }


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids", new_callable=AsyncMock)
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_empty_services(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context handles empty service data correctly."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = []
    mock_fetch_escalation_policy_ids.return_value = []

    context = await users.build_user_context()
    assert context == {
        "user_id": str(mock_user_parsed["id"]),
        "name": mock_user_parsed.get("name", ""),
        "email": mock_user_parsed.get("email", ""),
        "team_ids": ["team1"],
        "service_ids": [],
        "escalation_policy_ids": [],
    }


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids", new_callable=AsyncMock)
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_empty_escalation_policies(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context handles empty escalation policy data correctly."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    mock_fetch_escalation_policy_ids.return_value = []

    context = await users.build_user_context()
    assert context == {
        "user_id": str(mock_user_parsed["id"]),
        "name": mock_user_parsed.get("name", ""),
        "email": mock_user_parsed.get("email", ""),
        "team_ids": ["team1"],
        "service_ids": ["service1"],
        "escalation_policy_ids": [],
    }


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_invalid_team_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context raises RuntimeError for invalid team IDs."""
    mock_show_current_user.return_value = mock_user_parsed
    error = RuntimeError("Invalid team IDs")
    mock_fetch_team_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        await users.build_user_context()
    assert exc_info.value == error


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids", new_callable=AsyncMock)
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_invalid_service_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context raises RuntimeError for invalid service IDs."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_team_ids.return_value = ["team1"]
    error = RuntimeError("Invalid service IDs")
    mock_fetch_service_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        await users.build_user_context()
    assert exc_info.value == error


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids", new_callable=AsyncMock)
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_invalid_escalation_policy_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context raises RuntimeError for invalid escalation policy IDs."""
    mock_show_current_user.return_value = mock_user_parsed
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    error = RuntimeError("Invalid escalation policy IDs")
    mock_fetch_escalation_policy_ids.side_effect = error

    with pytest.raises(RuntimeError) as exc_info:
        await users.build_user_context()
    assert exc_info.value == error


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user", new_callable=AsyncMock)
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch(
    "pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids",
    new_callable=AsyncMock,
)
async def test_build_user_context_team_fetch_error(
    mock_fetch_escalation_policy_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user_parsed,
):
    """Test that build_user_context raises RuntimeError for team fetch errors."""
    mock_show_current_user.return_value = mock_user_parsed
    error = RuntimeError("API Error")
    mock_fetch_team_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        await users.build_user_context()
    assert exc_info.value == error


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_current_user_preserves_full_error_message(mock_get_api_client):
    """Test that show_current_user preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid user ID format"]}}'
    mock_error = ApiRuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.jget.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        await users._show_current_user()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_list_users_with_include(mock_get_api_client, mock_users):
    """Test that users can be filtered to include only specific fields."""
    mock_get_api_client.iter_all.return_value = mock_users

    user_list = await users.list_users(include=["id", "email"])

    assert len(user_list["users"]) > 0
    for user in user_list["users"]:
        assert "id" in user
        assert "email" in user
        assert len(user.keys()) == 2


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.users
async def test_show_user_with_include(mock_get_api_client, mock_users):
    """Test that a single user can be filtered to include only specific fields."""
    user_id = mock_users[0]["id"]
    mock_get_api_client.jget.return_value = {"user": mock_users[0]}

    user = await users.show_user(user_id=user_id, include=["id"])

    assert "id" in user["user"][0]
    assert len(user["user"][0].keys()) == 1
