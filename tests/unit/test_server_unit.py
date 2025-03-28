import pytest

from pagerduty_mcp_server import server

@pytest.mark.unit
@pytest.mark.server
def test_server():
    """Test that the server initializes correctly."""
    assert server.name == 'pagerduty_mcp_server'
