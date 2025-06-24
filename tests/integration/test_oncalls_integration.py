"""Integration tests for the oncalls module."""

import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import oncalls


@pytest.mark.integration
@pytest.mark.oncalls
@skip_if_no_pagerduty_key
def test_list_oncalls(user_context):
    """Test that oncalls are fetched correctly."""
    user_ids = [user_context["user_id"]]
    escalation_policy_ids = user_context["escalation_policy_ids"]

    oncalls_list = oncalls.list_oncalls(
        user_ids=user_ids, escalation_policy_ids=escalation_policy_ids, limit=1
    )
    assert oncalls_list is not None
    assert len(oncalls_list) > 0
