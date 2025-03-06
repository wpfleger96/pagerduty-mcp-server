from pagerduty_mcp_server import server

def test_server():
    """Test that the server initializes correctly."""
    assert server.name == 'pagerduty_mcp_server'
