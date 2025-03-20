import pytest

from conftest import skip_if_no_pagerduty_key
from pagerduty_mcp_server import escalation_policies
from pagerduty_mcp_server import utils

@pytest.mark.integration
@pytest.mark.escalation_policies
@skip_if_no_pagerduty_key
def test_list_escalation_policies():
    """Test that valid escalation policies are listed correctly."""
    user_context = utils.build_user_context()
    team_ids = user_context['team_ids']

    escalation_policy_list = escalation_policies.list_escalation_policies(team_ids=team_ids)
    assert escalation_policy_list is not None
    assert escalation_policy_list['metadata']['count'] > 0
    assert escalation_policy_list['escalation_policies'] is not None
    assert len(escalation_policy_list['escalation_policies']) > 0
