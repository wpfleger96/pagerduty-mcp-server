import pytest

from conftest import skip_if_no_pagerduty_key
from pagerduty_mcp_server import services
from pagerduty_mcp_server import utils

@pytest.mark.integration
@pytest.mark.services
@skip_if_no_pagerduty_key
def test_list_services():
    """Test that services are listed correctly."""
    user_context = utils.build_user_context()
    team_ids = user_context['team_ids']

    service_list = services.list_services(team_ids=team_ids)
    assert service_list is not None
    assert len(service_list) > 0
