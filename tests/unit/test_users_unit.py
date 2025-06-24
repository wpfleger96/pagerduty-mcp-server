"""Unit tests for the users module."""

from unittest.mock import MagicMock, patch

import pytest

from pagerduty_mcp_server import users, utils
from pagerduty_mcp_server.parsers.user_parser import parse_user


@pytest.mark.unit
@pytest.mark.users
def test_list_users(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that users are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_users

    user_list = users.list_users()

    mock_get_api_client.list_all.assert_called_once_with(users.USERS_URL, params={})
    assert user_list == utils.api_response_handler(
        results=[parse_user(result=user) for user in mock_users], resource_name="users"
    )


@pytest.mark.unit
@pytest.mark.users
def test_list_users_with_query(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that users can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.list_all.return_value = mock_users

    user_list = users.list_users(query=query)

    mock_get_api_client.list_all.assert_called_once_with(
        users.USERS_URL, params={"query": query}
    )
    assert user_list == utils.api_response_handler(
        results=[parse_user(result=user) for user in mock_users], resource_name="users"
    )


@pytest.mark.unit
@pytest.mark.users
def test_list_users_api_error(mock_get_api_client):
    """Test that list_users handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        users.list_users()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.users
def test_list_users_empty_response(mock_get_api_client):
    """Test that list_users handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    user_list = users.list_users()
    assert user_list == utils.api_response_handler(results=[], resource_name="users")


@pytest.mark.unit
@pytest.mark.users
def test_show_user(mock_get_api_client, mock_users):
    """Test that a single user is fetched correctly."""
    user_id = mock_users[0]["id"]
    mock_get_api_client.jget.return_value = {"user": mock_users[0]}

    user = users.show_user(user_id=user_id)

    mock_get_api_client.jget.assert_called_once_with(f"{users.USERS_URL}/{user_id}")
    assert user == utils.api_response_handler(
        results=parse_user(result=mock_users[0]), resource_name="user"
    )


@pytest.mark.unit
@pytest.mark.users
def test_show_user_invalid_id(mock_get_api_client):
    """Test that show_user raises ValueError for invalid user ID."""
    with pytest.raises(ValueError) as exc_info:
        users.show_user(user_id=None)
    assert str(exc_info.value) == "User ID is required"


@pytest.mark.unit
@pytest.mark.users
def test_show_user_api_error(mock_get_api_client):
    """Test that show_user handles API errors correctly."""
    user_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        users.show_user(user_id=user_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.users
def test_show_user_invalid_response(mock_get_api_client):
    """Test that show_user handles invalid API response correctly."""
    user_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'user' key

    with pytest.raises(RuntimeError) as exc_info:
        users.show_user(user_id=user_id)
    assert (
        str(exc_info.value) == "Failed to fetch user 123: Response missing 'user' field"
    )


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.users
def test_parse_user(mock_users, mock_users_parsed):
    """Test that parse_user correctly parses raw user data."""
    parsed_user = parse_user(result=mock_users[0])
    assert parsed_user == mock_users_parsed[0]


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.users
def test_parse_user_none():
    """Test that parse_user handles None input correctly."""
    assert parse_user(result=None) == {}


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_show_current_user,
    mock_user,
    mock_team_ids,
    mock_service_ids,
    mock_escalation_policy_ids,
):
    """Test that the user context is built correctly with all data present."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_service_ids.return_value = mock_service_ids
    mock_fetch_escalation_policy_ids.return_value = mock_escalation_policy_ids
    user_context = users.build_user_context()

    assert user_context["user_id"] == mock_user["id"]
    assert user_context["name"] == mock_user.get("name", "")
    assert user_context["email"] == mock_user.get("email", "")
    assert user_context["team_ids"] == mock_team_ids
    assert user_context["service_ids"] == mock_service_ids
    assert user_context["escalation_policy_ids"] == mock_escalation_policy_ids


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
def test_build_user_context_missing_data(mock_show_current_user):
    """Test that build_user_context raises ValueError for missing data."""
    mock_show_current_user.return_value = None

    with pytest.raises(ValueError) as exc_info:
        users.build_user_context()
    assert str(exc_info.value) == "Failed to get current user data"


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
def test_build_user_context_error_handling(mock_show_current_user):
    """Test that build_user_context raises RuntimeError for API errors."""
    error = RuntimeError("API Error")
    mock_show_current_user.side_effect = error

    with pytest.raises(RuntimeError) as exc_info:
        users.build_user_context()
    assert exc_info.value == error


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
def test_build_user_context_none_user(mock_show_current_user):
    """Test that build_user_context raises ValueError for None user data."""
    mock_show_current_user.return_value = None

    with pytest.raises(ValueError) as exc_info:
        users.build_user_context()
    assert str(exc_info.value) == "Failed to get current user data"


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_empty_teams(
    mock_fetch_escalation_policy_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context handles empty team data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = []
    mock_fetch_escalation_policy_ids.return_value = []

    context = users.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "name": mock_user.get("name", ""),
        "email": mock_user.get("email", ""),
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": [],
    }


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_empty_services(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context handles empty service data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = []
    mock_fetch_escalation_policy_ids.return_value = []

    context = users.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "name": mock_user.get("name", ""),
        "email": mock_user.get("email", ""),
        "team_ids": ["team1"],
        "service_ids": [],
        "escalation_policy_ids": [],
    }


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_empty_escalation_policies(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context handles empty escalation policy data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    mock_fetch_escalation_policy_ids.return_value = []

    context = users.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "name": mock_user.get("name", ""),
        "email": mock_user.get("email", ""),
        "team_ids": ["team1"],
        "service_ids": ["service1"],
        "escalation_policy_ids": [],
    }


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_invalid_team_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context raises RuntimeError for invalid team IDs."""
    mock_show_current_user.return_value = mock_user
    error = RuntimeError("Invalid team IDs")
    mock_fetch_team_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        users.build_user_context()
    assert exc_info.value == error


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_invalid_service_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context raises RuntimeError for invalid service IDs."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    error = RuntimeError("Invalid service IDs")
    mock_fetch_service_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        users.build_user_context()
    assert exc_info.value == error


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_invalid_escalation_policy_ids(
    mock_fetch_escalation_policy_ids,
    mock_fetch_service_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context raises RuntimeError for invalid escalation policy IDs."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    error = RuntimeError("Invalid escalation policy IDs")
    mock_fetch_escalation_policy_ids.side_effect = error

    with pytest.raises(RuntimeError) as exc_info:
        users.build_user_context()
    assert exc_info.value == error


@pytest.mark.unit
@pytest.mark.users
@patch("pagerduty_mcp_server.users._show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_team_fetch_error(
    mock_fetch_escalation_policy_ids,
    mock_fetch_team_ids,
    mock_show_current_user,
    mock_user,
):
    """Test that build_user_context raises RuntimeError for team fetch errors."""
    mock_show_current_user.return_value = mock_user
    error = RuntimeError("API Error")
    mock_fetch_team_ids.side_effect = error
    mock_fetch_escalation_policy_ids.return_value = []

    with pytest.raises(RuntimeError) as exc_info:
        users.build_user_context()
    assert exc_info.value == error


@pytest.mark.unit
@pytest.mark.users
def test_show_current_user_preserves_full_error_message(mock_get_api_client):
    """Test that show_current_user preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid user ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.jget.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        users._show_current_user()
    assert str(exc_info.value) == "API Error"
