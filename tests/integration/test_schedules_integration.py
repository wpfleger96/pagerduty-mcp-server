import pytest

from pagerduty_mcp_server import schedules

@pytest.mark.integration
@pytest.mark.schedules
def test_list_schedules():
    """Test that schedules are fetched correctly."""
    schedules_list = schedules.list_schedules()
    assert schedules_list is not None
    assert len(schedules_list) > 0
