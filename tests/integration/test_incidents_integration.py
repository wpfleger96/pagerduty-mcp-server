from datetime import datetime, timedelta

import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import incidents


@pytest.mark.integration
@pytest.mark.incidents
@skip_if_no_pagerduty_key
def test_list_incidents(user_context):
    """Test that incidents are fetched correctly."""
    team_ids = user_context["team_ids"]

    since = (datetime.now() - timedelta(days=1)).isoformat()
    until = datetime.now().isoformat()
    incidents_list = incidents.list_incidents(
        team_ids=team_ids, limit=1, since=since, until=until
    )
    assert incidents_list is not None
    assert len(incidents_list) > 0
