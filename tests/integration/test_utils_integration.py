import pytest

from conftest import skip_if_no_pagerduty_key
from pagerduty_mcp_server import utils

@pytest.mark.integration
@pytest.mark.utils
@skip_if_no_pagerduty_key
def test_build_user_context():
    """Test that the user context is built correctly."""
    user_context = utils.build_user_context()

    assert user_context is not None
    assert user_context['user_id'] is not None
    assert user_context['team_ids'] is not None
    assert user_context['service_ids'] is not None
    assert user_context['escalation_policy_ids'] is not None
