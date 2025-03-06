from pagerduty_mcp_server import users
from conftest import skip_if_no_pagerduty_key

@skip_if_no_pagerduty_key
def test_show_current_user():
    """Test that the current user is displayed correctly."""