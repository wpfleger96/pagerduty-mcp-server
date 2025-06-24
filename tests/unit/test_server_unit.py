import pytest

from pagerduty_mcp_server import mcp


@pytest.mark.unit
@pytest.mark.server
def test_mcp():
    """Test that the server initializes correctly."""
    assert mcp.name == "pagerduty_mcp_server"
