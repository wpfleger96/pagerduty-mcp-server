"""Unit tests for the utils module."""

import pytest
from unittest.mock import patch

from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context(mock_fetch_escalation_policy_ids, mock_fetch_service_ids, mock_show_current_user, mock_user, mock_team_ids, mock_service_ids, mock_escalation_policy_ids):
    """Test that the user context is built correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_service_ids.return_value = mock_service_ids
    mock_fetch_escalation_policy_ids.return_value = mock_escalation_policy_ids
    user_context = utils.build_user_context()

    assert user_context['user_id'] == mock_user["id"]
    assert user_context['team_ids'] == mock_team_ids
    assert user_context['service_ids'] == mock_service_ids
    assert user_context['escalation_policy_ids'] == mock_escalation_policy_ids

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
def test_build_user_context_user_error(mock_show_current_user):
    """Test that build_user_context handles user fetch errors correctly."""
    mock_show_current_user.side_effect = RuntimeError("Failed to fetch user")
    
    with pytest.raises(RuntimeError) as exc_info:
        utils.build_user_context()
    assert str(exc_info.value) == "Failed to fetch user"

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
def test_build_user_context_service_error(mock_fetch_service_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles service fetch errors correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_service_ids.side_effect = RuntimeError("Failed to fetch services")
    
    with pytest.raises(RuntimeError) as exc_info:
        utils.build_user_context()
    assert str(exc_info.value) == "Failed to fetch services"

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_escalation_error(mock_fetch_escalation_policy_ids, mock_fetch_service_ids, mock_show_current_user, mock_user, mock_team_ids, mock_service_ids):
    """Test that build_user_context handles escalation policy fetch errors correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_service_ids.return_value = mock_service_ids
    mock_fetch_escalation_policy_ids.side_effect = RuntimeError("Failed to fetch escalation policies")
    
    with pytest.raises(RuntimeError) as exc_info:
        utils.build_user_context()
    assert str(exc_info.value) == "Failed to fetch escalation policies"
