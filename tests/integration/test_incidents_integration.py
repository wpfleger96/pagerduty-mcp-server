from datetime import UTC, datetime, timedelta

import pytest

from pagerduty_mcp_server import incidents
from tests.conftest import skip_if_no_pagerduty_key


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.incidents
@skip_if_no_pagerduty_key
async def test_list_incidents(user_context):
    """Test that incidents are fetched correctly."""
    team_ids = user_context["team_ids"]

    since = (datetime.now(tz=UTC) - timedelta(days=1)).isoformat()
    until = datetime.now(tz=UTC).isoformat()
    incidents_list = await incidents.list_incidents(
        team_ids=team_ids, limit=1, since=since, until=until
    )
    assert incidents_list is not None
    assert len(incidents_list) > 0
