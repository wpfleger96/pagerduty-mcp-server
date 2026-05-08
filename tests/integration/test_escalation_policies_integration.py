import pytest
from tests.conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import escalation_policies


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.escalation_policies
@skip_if_no_pagerduty_key
async def test_list_escalation_policies(user_context):
    """Test that escalation policies are fetched correctly."""
    user_ids = [user_context["user_id"]]
    team_ids = user_context["team_ids"]

    policies = await escalation_policies.list_escalation_policies(
        user_ids=user_ids, team_ids=team_ids, limit=1
    )
    assert policies is not None
    assert len(policies) > 0
