import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import services


@pytest.mark.integration
@pytest.mark.services
@skip_if_no_pagerduty_key
def test_list_services(user_context):
    """Test that services are fetched correctly."""
    team_ids = user_context["team_ids"]

    services_list = services.list_services(team_ids=team_ids, limit=1)
    assert services_list is not None
    assert len(services_list) > 0
