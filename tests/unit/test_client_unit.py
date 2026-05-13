from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request

from pagerduty_mcp_server.client import PagerDutyClient, create_client
from pagerduty_mcp_server.errors import PagerDutyAuthError


@pytest.fixture(autouse=True)
def reset_env_client():
    """Reset the singleton env client before and after each test."""
    from pagerduty_mcp_server.client import client as module_client

    module_client._env_client = None
    PagerDutyClient._env_client = None
    module_client._env_token = None
    PagerDutyClient._env_token = None
    yield
    module_client._env_client = None
    PagerDutyClient._env_client = None
    module_client._env_token = None
    PagerDutyClient._env_token = None


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_request_token():
    """Test that create_client() creates new instance with request token."""
    mock_client = MagicMock()

    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-PagerDuty-Token": "request-token"}

    with patch(
        "pagerduty_mcp_server.client._RestClient", return_value=mock_client
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                create_client()
                create_client()

                assert mock_client_class.call_count == 2
                mock_client_class.assert_called_with("request-token")


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_env_token_singleton():
    """Test that create_client() reuses instance with env token."""
    mock_client = MagicMock()

    with patch(
        "pagerduty_mcp_server.client._RestClient", return_value=mock_client
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", side_effect=RuntimeError
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                client1 = create_client()
                client2 = create_client()

                mock_client_class.assert_called_once_with("env-token")
                assert client1 is client2


@pytest.mark.unit
@pytest.mark.client
def test_token_precedence():
    """Test that header token takes precedence over env token."""
    mock_header_client = MagicMock()
    mock_env_client = MagicMock()

    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-PagerDuty-Token": "header-token"}

    with patch(
        "pagerduty_mcp_server.client._RestClient",
        side_effect=[mock_header_client, mock_env_client],
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                create_client()

                mock_client_class.assert_called_once_with("header-token")


@pytest.mark.unit
@pytest.mark.client
def test_create_client_no_token(monkeypatch):
    """Test that create_client() raises exception when no token is available."""
    # Ensure singleton is reset
    PagerDutyClient._env_client = None

    # Remove any environment variables
    monkeypatch.delenv("PAGERDUTY_API_TOKEN", raising=False)

    # Mock request with no token
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {}  # Empty headers, no token

    # Create a fresh instance to avoid any class-level caching
    test_client = PagerDutyClient()

    with patch("pagerduty_mcp_server.client._RestClient") as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            # Verify our setup is clean
            assert test_client._env_client is None
            assert PagerDutyClient._env_client is None
            assert test_client._get_request_token() == (True, None)
            assert test_client._get_env_token() is None

            # Test the error is raised
            with pytest.raises(PagerDutyAuthError) as exc_info:
                test_client.get_client()

            # In request context with no token the request-context error fires first
            assert "PagerDuty credentials are not configured for this request" in str(
                exc_info.value
            )
            mock_client_class.assert_not_called()


@pytest.mark.unit
@pytest.mark.client
def test_get_request_token():
    """Test request token retrieval from HTTP header."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-PagerDuty-Token": "header-token"}

    with patch(
        "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
    ):
        has_context, token = PagerDutyClient._get_request_token()
        assert has_context is True
        assert token == "header-token"


@pytest.mark.unit
@pytest.mark.client
def test_get_request_token_missing():
    """Test request token retrieval when header is absent."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {}

    with patch(
        "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
    ):
        has_context, token = PagerDutyClient._get_request_token()
        assert has_context is True
        assert token is None


@pytest.mark.unit
@pytest.mark.client
def test_get_env_token():
    """Test environment token retrieval."""
    with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
        token = PagerDutyClient._get_env_token()
        assert token == "env-token"


@pytest.mark.unit
@pytest.mark.client
def test_get_env_token_missing():
    """Test environment token retrieval when missing."""
    with patch.dict("os.environ", {}, clear=True):
        token = PagerDutyClient._get_env_token()
        assert token is None


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_token():
    """Test client creation with token."""
    mock_client = MagicMock()

    with patch(
        "pagerduty_mcp_server.client._RestClient", return_value=mock_client
    ) as mock_client_class:
        PagerDutyClient._create_client_with_token("test-token")

        mock_client_class.assert_called_once_with("test-token")


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_bearer_token():
    """Test that tokens with pdus+_ prefix use bearer auth_type."""
    mock_client = MagicMock()
    bearer_token = "pdus+_abc123xyz"

    with patch(
        "pagerduty_mcp_server.client._RestClient", return_value=mock_client
    ) as mock_client_class:
        PagerDutyClient._create_client_with_token(bearer_token)

        mock_client_class.assert_called_once_with(bearer_token, auth_type="bearer")


@pytest.mark.unit
@pytest.mark.client
def test_get_oauth_token_returns_none_when_no_client_id(monkeypatch):
    """Test that _get_oauth_token returns None when no client ID is configured."""
    monkeypatch.delenv("PAGERDUTY_CLIENT_ID", raising=False)

    with patch("pagerduty_mcp_server.auth.DEFAULT_CLIENT_ID", ""):
        result = PagerDutyClient._get_oauth_token()

    assert result is None


@pytest.mark.unit
@pytest.mark.client
def test_env_client_recreated_on_token_rotation():
    """Test that env client is recreated when PAGERDUTY_API_TOKEN changes."""
    mock_client_a = MagicMock()
    mock_client_b = MagicMock()

    with patch(
        "pagerduty_mcp_server.client._RestClient",
        side_effect=[mock_client_a, mock_client_b],
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", side_effect=RuntimeError
        ):
            # First call with token "a"
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "token-a"}):
                client1 = create_client()
                assert client1 is mock_client_a
                mock_client_class.assert_called_once_with("token-a")

            # Second call with different token "b"
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "token-b"}):
                client2 = create_client()
                assert client2 is mock_client_b
                assert mock_client_class.call_count == 2


@pytest.mark.unit
@pytest.mark.client
def test_get_oauth_token_raises_auth_error_on_failure(monkeypatch):
    """Test that _get_oauth_token raises PagerDutyAuthError when OAuth flow fails."""
    monkeypatch.setenv("PAGERDUTY_CLIENT_ID", "test-client-id")

    with patch(
        "pagerduty_mcp_server.client.PagerDutyClient._get_oauth_token"
    ) as mock_oauth:
        mock_oauth.side_effect = PagerDutyAuthError(
            "OAuth authorization failed: access_denied"
        )

        with pytest.raises(PagerDutyAuthError) as exc_info:
            mock_oauth()

        assert "OAuth authorization failed" in str(exc_info.value)
