import logging
import os
from importlib.metadata import version
from typing import Optional

import pagerduty
from dotenv import load_dotenv
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from .errors import PagerDutyAuthError

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class _RestClient(pagerduty.RestApiV2Client):
    @property
    def user_agent(self) -> str:
        return f"pagerduty_mcp_server/{version('pagerduty_mcp_server')} {super().user_agent}"


class PagerDutyClient:
    _env_client: Optional[pagerduty.RestApiV2Client] = None
    _env_token: Optional[str] = None

    @staticmethod
    def _get_request_token() -> tuple:
        """Try to get auth token from the active HTTP request.

        Returns:
            tuple[bool, Optional[str]]: A tuple of (has_request_context, token)
        """
        try:
            request: Request = get_http_request()
            return True, request.headers.get("X-PagerDuty-Token")
        except RuntimeError:
            return False, None

    @staticmethod
    def _get_oauth_token() -> Optional[str]:
        """Try to get OAuth token from keyring or run interactive OAuth flow for local use.

        OAuth is configured if either:
        - PAGERDUTY_CLIENT_ID environment variable is set, OR
        - DEFAULT_CLIENT_ID in auth.py has been updated from placeholder

        Returns:
            Optional[str]: The token if OAuth succeeds, None if OAuth not configured

        Raises:
            PagerDutyAuthError: If OAuth is configured but fails (e.g., user denies access)
        """
        from .auth import DEFAULT_CLIENT_ID

        client_id = os.environ.get("PAGERDUTY_CLIENT_ID", DEFAULT_CLIENT_ID)
        if not client_id:
            logger.debug("OAuth not configured (no client ID available)")
            return None

        try:
            from .auth import get_token

            return get_token()
        except Exception as e:
            logger.error(f"OAuth authentication failed: {e}")
            raise PagerDutyAuthError(str(e)) from e

    @staticmethod
    def _get_env_token() -> Optional[str]:
        """Try to get auth token from environment variable.

        Returns:
            Optional[str]: The token if found in environment, None otherwise
        """
        return os.environ.get("PAGERDUTY_API_TOKEN")

    @staticmethod
    def _create_client_with_token(token: str) -> pagerduty.RestApiV2Client:
        """Create a new PagerDuty client with the given token.

        Args:
            token: The authentication token to use

        Returns:
            pagerduty.RestApiV2Client: A configured client
        """
        if token.startswith("pdus+_"):
            return _RestClient(token, auth_type="bearer")
        return _RestClient(token)

    def get_client(self) -> pagerduty.RestApiV2Client:
        """Get a PagerDuty API client.

        Authentication priority:
        1. X-PagerDuty-Token HTTP header (platform/server integration)
        2. PAGERDUTY_API_TOKEN environment variable (if explicitly set)
        3. OAuth token from keyring (local interactive use only)

        Returns:
            pagerduty.RestApiV2Client: A configured PagerDuty API client

        Raises:
            PagerDutyAuthError: If no valid auth token is found
        """
        has_request_context, request_token = self._get_request_token()

        if request_token:
            return self._create_client_with_token(request_token)

        if current_token := self._get_env_token():
            if (
                PagerDutyClient._env_client is None
                or PagerDutyClient._env_token != current_token
            ):
                logger.info("Using PAGERDUTY_API_TOKEN environment variable")
                PagerDutyClient._env_client = self._create_client_with_token(
                    current_token
                )
                PagerDutyClient._env_token = current_token
            return PagerDutyClient._env_client

        if has_request_context:
            message = "PagerDuty credentials are not configured for this request. Provide X-PagerDuty-Token header or set PAGERDUTY_API_TOKEN."
            logger.error(message)
            raise PagerDutyAuthError(message)

        if token := self._get_oauth_token():
            return self._create_client_with_token(token)

        message = "No auth token found. Set PAGERDUTY_API_TOKEN or authenticate locally via OAuth."
        logger.error(message)
        raise PagerDutyAuthError(message)


# Singleton instance
client = PagerDutyClient()


def create_client() -> pagerduty.RestApiV2Client:
    """Get a PagerDuty API client.

    Authentication priority:
    1. X-PagerDuty-Token HTTP header (platform/server integration)
    2. PAGERDUTY_API_TOKEN environment variable (if explicitly set)
    3. OAuth token from keyring (local interactive use only)

    Returns:
        pagerduty.RestApiV2Client: A configured PagerDuty API client

    Raises:
        PagerDutyAuthError: If no valid auth token is found
    """
    return client.get_client()
