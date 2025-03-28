import pytest

from pagerduty_mcp_server import escalation_policies
from pagerduty_mcp_server.parsers import parse_escalation_policy
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies(mock_get_api_client, mock_escalation_policies):
    """Test that escalation policies are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_escalation_policies

    policy_list = escalation_policies.list_escalation_policies()

    mock_get_api_client.list_all.assert_called_once_with(escalation_policies.ESCALATION_POLICIES_URL, params={})
    assert policy_list == utils.api_response_handler(results=[parse_escalation_policy(result=policy) for policy in mock_escalation_policies], resource_name='escalation_policies')

@pytest.mark.unit
@pytest.mark.escalation_policies
def test_fetch_escalation_policy_ids(mock_get_api_client, mock_escalation_policies, mock_user):
    """Test that escalation policy IDs are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_escalation_policies

    policy_ids = escalation_policies.fetch_escalation_policy_ids(user_id=mock_user['id'])

    mock_get_api_client.list_all.assert_called_once_with(escalation_policies.ESCALATION_POLICIES_URL, params={'user_ids[]': [mock_user['id']]})
    assert set(policy_ids) == set([policy['id'] for policy in mock_escalation_policies])

@pytest.mark.unit
@pytest.mark.escalation_policies
def test_show_escalation_policy(mock_get_api_client, mock_escalation_policies):
    """Test that an escalation policy is fetched correctly."""
    mock_get_api_client.jget.return_value = {'escalation_policy': mock_escalation_policies[0]}

    policy = escalation_policies.show_escalation_policy(policy_id=mock_escalation_policies[0])
    assert policy == utils.api_response_handler(results=parse_escalation_policy(result=mock_escalation_policies[0]), resource_name='escalation_policy')

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.escalation_policies
def test_parse_escalation_policy(mock_escalation_policies, mock_escalation_policies_parsed):
    """Test that an escalation policy is parsed correctly."""
    parsed_policy = parse_escalation_policy(result=mock_escalation_policies[0])
    assert parsed_policy == mock_escalation_policies_parsed[0]
