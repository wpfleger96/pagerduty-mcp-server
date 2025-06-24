import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import teams


@pytest.mark.integration
@pytest.mark.teams
@skip_if_no_pagerduty_key
def test_list_teams():
    """Test that teams are fetched correctly."""
    teams_list = teams.list_teams()
    assert teams_list is not None
    assert len(teams_list) > 0
