import pagerduty
import pytest
from conftest import skip_if_no_pagerduty_key

from pagerduty_mcp_server.client import create_client


@pytest.mark.integration
@pytest.mark.client
@skip_if_no_pagerduty_key
def test_get_api_client():
    """Test that the API client is created correctly."""
    test_client = create_client()

    assert isinstance(test_client, pagerduty.RestApiV2Client)
    assert test_client.api_key is not None
