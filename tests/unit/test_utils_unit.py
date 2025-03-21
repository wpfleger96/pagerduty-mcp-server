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
    """Test that the user context is built correctly with all data present."""
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
def test_build_user_context_missing_data(mock_show_current_user):
    """Test that build_user_context handles missing or invalid data correctly."""
    mock_show_current_user.return_value = None
    
    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
def test_build_user_context_error_handling(mock_show_current_user):
    """Test that build_user_context handles errors gracefully."""
    mock_show_current_user.side_effect = RuntimeError("API Error")

    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_single_result():
    """Test that api_response_handler formats a single result correctly."""
    result = {'id': '123', 'name': 'test'}
    response = utils.api_response_handler(
        results=result,
        resource_name='test'
    )

    assert response == {
        'metadata': {
            'count': 1,
            'description': 'Found 1 result for resource type test'
        },
        'test': [result]
    }

@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_multiple_results():
    """Test that api_response_handler formats multiple results correctly."""
    results = [
        {'id': '123', 'name': 'test1'},
        {'id': '456', 'name': 'test2'}
    ]
    response = utils.api_response_handler(
        results=results,
        resource_name='tests'
    )

    assert response == {
        'metadata': {
            'count': 2,
            'description': 'Found 2 results for resource type tests'
        },
        'tests': results
    }

@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_with_metadata():
    """Test that api_response_handler includes additional metadata."""
    result = {'id': '123', 'name': 'test'}
    additional_metadata = {'status': 'active'}
    response = utils.api_response_handler(
        results=result,
        resource_name='test',
        additional_metadata=additional_metadata
    )

    assert response['metadata']['status'] == 'active'

@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_limit_exceeded():
    """Test that api_response_handler handles limit exceeded correctly."""
    results = [{'id': str(i)} for i in range(utils.RESPONSE_LIMIT + 50)]
    response = utils.api_response_handler(
        results=results,
        resource_name='tests',
        limit=utils.RESPONSE_LIMIT
    )

    assert 'error' in response
    assert response['error']['code'] == 'LIMIT_EXCEEDED'
    assert f'exceeds the limit of {utils.RESPONSE_LIMIT}' in response['error']['message']

@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_empty_resource_name():
    """Test that api_response_handler raises ValidationError for empty resource_name."""
    with pytest.raises(utils.ValidationError) as exc_info:
        utils.api_response_handler(
            results={'id': '123'},
            resource_name=''
        )
    assert str(exc_info.value) == "resource_name cannot be empty"

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
def test_build_user_context_empty_user(mock_show_current_user):
    """Test that build_user_context handles empty user data correctly."""
    mock_show_current_user.return_value = {}

    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
def test_build_user_context_none_user(mock_show_current_user):
    """Test that build_user_context handles None user data correctly."""
    mock_show_current_user.return_value = None

    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
def test_build_user_context_empty_teams(mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles empty team data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = []

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
def test_build_user_context_empty_services(mock_fetch_service_ids, mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles empty service data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = []

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": ["team1"],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_empty_escalation_policies(mock_fetch_escalation_policy_ids, mock_fetch_service_ids, mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles empty escalation policy data correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    mock_fetch_escalation_policy_ids.return_value = []

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": ["team1"],
        "service_ids": ["service1"],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_all_empty(mock_fetch_escalation_policy_ids, mock_fetch_service_ids, mock_fetch_team_ids, mock_show_current_user):
    """Test that build_user_context handles all empty data correctly."""
    mock_show_current_user.return_value = {}
    mock_fetch_team_ids.return_value = []
    mock_fetch_service_ids.return_value = []
    mock_fetch_escalation_policy_ids.return_value = []

    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
def test_build_user_context_invalid_user_id(mock_show_current_user):
    """Test that build_user_context handles invalid user ID correctly."""
    mock_show_current_user.return_value = {"id": None}

    context = utils.build_user_context()
    assert context == {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
def test_build_user_context_invalid_team_ids(mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles invalid team IDs correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = [None, "", 123]  # Mix of invalid types

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
def test_build_user_context_invalid_service_ids(mock_fetch_service_ids, mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles invalid service IDs correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = [None, "", 123]  # Mix of invalid types

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": ["team1"],
        "service_ids": [],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
@patch("pagerduty_mcp_server.services.fetch_service_ids")
@patch("pagerduty_mcp_server.escalation_policies.fetch_escalation_policy_ids")
def test_build_user_context_invalid_escalation_policy_ids(mock_fetch_escalation_policy_ids, mock_fetch_service_ids, mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles invalid escalation policy IDs correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.return_value = ["team1"]
    mock_fetch_service_ids.return_value = ["service1"]
    mock_fetch_escalation_policy_ids.return_value = [None, "", 123]  # Mix of invalid types

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": ["team1"],
        "service_ids": ["service1"],
        "escalation_policy_ids": []
    }

@pytest.mark.unit
@pytest.mark.utils
@patch("pagerduty_mcp_server.users.show_current_user")
@patch("pagerduty_mcp_server.teams.fetch_team_ids")
def test_build_user_context_team_fetch_error(mock_fetch_team_ids, mock_show_current_user, mock_user):
    """Test that build_user_context handles team fetch errors correctly."""
    mock_show_current_user.return_value = mock_user
    mock_fetch_team_ids.side_effect = Exception("API Error")

    context = utils.build_user_context()
    assert context == {
        "user_id": str(mock_user["id"]),
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }
