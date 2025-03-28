import pytest

from pagerduty_mcp_server import incidents
from pagerduty_mcp_server import utils

@pytest.mark.integration
@pytest.mark.incidents
def test_list_incidents():
    """Test that incidents are fetched correctly."""
    user_context = utils.build_user_context()
    team_ids = user_context['team_ids']

    incidents_list = incidents.list_incidents(team_ids=team_ids)
    assert incidents_list is not None
    assert len(incidents_list) > 0
