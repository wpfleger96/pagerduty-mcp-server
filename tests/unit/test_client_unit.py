from importlib.metadata import version
from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request

from pagerduty_mcp_server.client import PagerDutyClient, create_client


@pytest.fixture(autouse=True)
def reset_env_client():
    """Reset the singleton env client before each test."""
    PagerDutyClient._env_client = None
    yield


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_request_token():
    """Test that create_client() creates new instance with request token."""
    # Create mock client with headers attribute
    mock_client = MagicMock()
    mock_client.headers = {}

    # Create mock request with token
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-Goose-Token": "request-token"}

    with patch(
        "pagerduty.RestApiV2Client", return_value=mock_client
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                client1 = create_client()
                client2 = create_client()

                # Verify new instance created each time with request token
                assert mock_client_class.call_count == 2
                mock_client_class.assert_called_with("request-token")
                assert (
                    client1.headers["User-Agent"]
                    == f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
                )
                assert (
                    client2.headers["User-Agent"]
                    == f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
                )


@pytest.mark.unit
@pytest.mark.client
def test_create_client_with_env_token_singleton():
    """Test that create_client() reuses instance with env token."""
    # Create mock client with headers attribute
    mock_client = MagicMock()
    mock_client.headers = {}

    with patch(
        "pagerduty.RestApiV2Client", return_value=mock_client
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", side_effect=RuntimeError
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                client1 = create_client()
                client2 = create_client()

                # Verify single instance created and reused
                mock_client_class.assert_called_once_with("env-token")
                assert client1 is client2
                assert (
                    client1.headers["User-Agent"]
                    == f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
                )


@pytest.mark.unit
@pytest.mark.client
def test_token_precedence():
    """Test that header token takes precedence over env token."""
    # Create mock clients with headers attribute
    mock_header_client = MagicMock()
    mock_header_client.headers = {}
    mock_env_client = MagicMock()
    mock_env_client.headers = {}

    # Create mock request with token
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-Goose-Token": "header-token"}

    with patch(
        "pagerduty.RestApiV2Client", side_effect=[mock_header_client, mock_env_client]
    ) as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            with patch.dict("os.environ", {"PAGERDUTY_API_TOKEN": "env-token"}):
                client = create_client()

                # Verify header token was used
                mock_client_class.assert_called_once_with("header-token")
                assert (
                    client.headers["User-Agent"]
                    == f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
                )


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

    with patch("pagerduty.RestApiV2Client") as mock_client_class:
        with patch(
            "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
        ):
            # Verify our setup is clean
            assert test_client._env_client is None
            assert PagerDutyClient._env_client is None
            assert test_client._get_header_token() is None
            assert test_client._get_env_token() is None

            # Test the error is raised
            with pytest.raises(Exception) as exc_info:
                test_client.get_client()

            assert (
                str(exc_info.value)
                == "No auth token found in headers or environment variables"
            )
            mock_client_class.assert_not_called()


@pytest.mark.unit
@pytest.mark.client
def test_get_header_token():
    """Test header token retrieval."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"X-Goose-Token": "header-token"}

    with patch(
        "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
    ):
        token = PagerDutyClient._get_header_token()
        assert token == "header-token"


@pytest.mark.unit
@pytest.mark.client
def test_get_header_token_missing():
    """Test header token retrieval when missing."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {}

    with patch(
        "pagerduty_mcp_server.client.get_http_request", return_value=mock_request
    ):
        token = PagerDutyClient._get_header_token()
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
    mock_client.headers = {}

    with patch(
        "pagerduty.RestApiV2Client", return_value=mock_client
    ) as mock_client_class:
        client = PagerDutyClient._create_client_with_token("test-token")

        mock_client_class.assert_called_once_with("test-token")
        assert (
            client.headers["User-Agent"]
            == f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
        )
