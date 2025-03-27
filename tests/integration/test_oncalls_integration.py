"""Integration tests for the oncalls module."""

import pytest

from pagerduty_mcp_server import escalation_policies
from pagerduty_mcp_server import oncalls
from pagerduty_mcp_server import utils

@pytest.mark.integration
@pytest.mark.oncalls
def test_list_oncalls():
    """Test that oncalls are fetched correctly."""
    user_context = utils.build_user_context()
    team_ids = user_context['team_ids']

    escalation_policy_response = escalation_policies.list_escalation_policies(
        team_ids=team_ids
    )
    escalation_policy_ids = [policy["id"] for policy in escalation_policy_response['escalation_policies']]

    oncalls_list = oncalls.list_oncalls(escalation_policy_ids=escalation_policy_ids)
    assert oncalls_list is not None
    assert len(oncalls_list) > 0
