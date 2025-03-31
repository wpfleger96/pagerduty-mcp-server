import pytest

from conftest import skip_if_no_pagerduty_key
from pagerduty_mcp_server import users

@pytest.mark.integration
@pytest.mark.users
@skip_if_no_pagerduty_key
def test_show_current_user():
    """Test that the current user is displayed correctly."""
    user = users.show_current_user()

    assert user is not None
    assert "id" in user

@pytest.mark.integration
@pytest.mark.users
@skip_if_no_pagerduty_key
def test_list_users(user_context):
    """Test that users are fetched correctly."""
    team_ids = user_context['team_ids']

    users_list = users.list_users(team_ids=team_ids, limit=1)
    assert users_list is not None
    assert len(users_list) > 0

@pytest.mark.integration
@pytest.mark.users
@skip_if_no_pagerduty_key
def test_show_user():
    """Test that a user is shown correctly."""
    current_user_id = users.show_current_user()["id"]
    response = users.show_user(user_id=current_user_id)

    assert response is not None
    assert "user" in response
    assert "metadata" in response
    assert response["user"][0]["id"] == current_user_id
