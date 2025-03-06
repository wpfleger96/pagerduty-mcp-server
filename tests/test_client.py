from pagerduty_mcp_server import client
from conftest import skip_if_no_pagerduty_key

@skip_if_no_pagerduty_key
def test_get_api_client():
    """Test that the API client is created correctly."""
    test_client = client.get_api_client()
    assert type(test_client) == pagerduty.RestApiV2Client
    assert test_client.api_key is not None
