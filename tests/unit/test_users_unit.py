"""Unit tests for the users module."""

import pytest

from pagerduty_mcp_server.parsers.user_parser import parse_user

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.users
def test_parse_user(mock_user, mock_user_parsed):
    """Test that parse_user correctly parses raw user data."""
    assert parse_user(result=mock_user) == mock_user_parsed
