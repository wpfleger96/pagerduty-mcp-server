import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server import schedules


@pytest.mark.integration
@pytest.mark.schedules
@skip_if_no_pagerduty_key
def test_list_schedules():
    """Test that schedules are fetched correctly."""

    schedules_list = schedules.list_schedules()
    assert schedules_list is not None
    assert len(schedules_list) > 0
