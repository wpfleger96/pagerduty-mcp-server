"""Unit tests for the users module."""

import pytest

from pagerduty_mcp_server import users
from pagerduty_mcp_server.parsers.user_parser import parse_user
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.users
def test_list_users(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that users are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_users

    user_list = users.list_users()

    mock_get_api_client.list_all.assert_called_once_with(users.USERS_URL, params={})
    assert user_list == utils.api_response_handler(results=[parse_user(result=user) for user in mock_users], resource_name='users')

@pytest.mark.unit
@pytest.mark.users
def test_list_users_with_query(mock_get_api_client, mock_users, mock_users_parsed):
    """Test that users can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.list_all.return_value = mock_users

    user_list = users.list_users(query=query)

    mock_get_api_client.list_all.assert_called_once_with(users.USERS_URL, params={'query': query})
    assert user_list == utils.api_response_handler(results=[parse_user(result=user) for user in mock_users], resource_name='users')

@pytest.mark.unit
@pytest.mark.users
def test_list_users_api_error(mock_get_api_client):
    """Test that list_users handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        users.list_users()
    assert str(exc_info.value) == "Failed to fetch users: API Error"

@pytest.mark.unit
@pytest.mark.users
def test_list_users_empty_response(mock_get_api_client):
    """Test that list_users handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    user_list = users.list_users()
    assert user_list == utils.api_response_handler(results=[], resource_name='users')

@pytest.mark.unit
@pytest.mark.users
def test_show_user(mock_get_api_client, mock_users):
    """Test that a single user is fetched correctly."""
    user_id = mock_users[0]['id']
    mock_get_api_client.jget.return_value = {'user': mock_users[0]}

    user = users.show_user(user_id=user_id)

    mock_get_api_client.jget.assert_called_once_with(f"{users.USERS_URL}/{user_id}")
    assert user == utils.api_response_handler(results=parse_user(result=mock_users[0]), resource_name='user')

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
    user_id = '123'
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        users.show_user(user_id=user_id)
    assert str(exc_info.value) == f"Failed to fetch user {user_id}: API Error"

@pytest.mark.unit
@pytest.mark.users
def test_show_user_invalid_response(mock_get_api_client):
    """Test that show_user handles invalid API response correctly."""
    user_id = '123'
    mock_get_api_client.jget.return_value = {}  # Missing 'user' key

    with pytest.raises(RuntimeError) as exc_info:
        users.show_user(user_id=user_id)
    assert str(exc_info.value) == f"Failed to fetch user {user_id}: 'user'"

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
