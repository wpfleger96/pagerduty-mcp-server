import base64
import hashlib
import logging
import os
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import keyring
import keyring.errors
import requests

from .errors import PagerDutyAuthError

logger = logging.getLogger(__name__)

DEFAULT_CLIENT_ID = ""

KEYRING_SERVICE = "pagerduty_mcp_server"
KEYRING_KEY_ACCESS_TOKEN = "oauth_token"
KEYRING_KEY_TOKEN_EXPIRY = "token_expiry"
KEYRING_KEY_REFRESH_TOKEN = "refresh_token"

OAUTH_TOKEN_URL = "https://identity.pagerduty.com/oauth/token"
OAUTH_AUTHORIZE_URL = "https://identity.pagerduty.com/oauth/authorize"


def _parse_callback_port() -> int:
    raw = os.environ.get("PAGERDUTY_OAUTH_CALLBACK_PORT", "5173")
    try:
        port = int(raw)
    except ValueError:
        logger.warning("Invalid PAGERDUTY_OAUTH_CALLBACK_PORT=%r, using 5173", raw)
        return 5173
    if not (1024 <= port <= 65535):
        logger.warning(
            "PAGERDUTY_OAUTH_CALLBACK_PORT=%d out of range, using 5173", port
        )
        return 5173
    return port


OAUTH_CALLBACK_PORT = _parse_callback_port()
OAUTH_REDIRECT_URI = f"http://localhost:{OAUTH_CALLBACK_PORT}/oauth/pagerduty"
OAUTH_SCOPE = "read write"

DEFAULT_TOKEN_EXPIRY_SECONDS = 86400  # 24 hours

OAUTH_CALLBACK_TIMEOUT_SECONDS = 30
OAUTH_TOTAL_TIMEOUT_SECONDS = 300

_get_token_lock = threading.Lock()


def safe_delete_password(service, username):
    """Safely delete a password from keyring, ignoring errors if it doesn't exist.

    Args:
        service: The service name for keyring storage
        username: The username/key for keyring storage
    """
    try:
        keyring.delete_password(service, username)
    except keyring.errors.PasswordDeleteError:
        pass


def generate_pkce_codes():
    """Generate PKCE code verifier and challenge for OAuth flow.

    Returns:
        tuple[str, str]: A tuple of (code_verifier, code_challenge)
    """
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(96)).rstrip(b"=").decode("utf-8")
    )
    challenge_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(challenge_hash).rstrip(b"=").decode("utf-8")
    )
    return code_verifier, code_challenge


def refresh_access_token(refresh_token):
    """Refresh an expired OAuth access token using a refresh token.

    Args:
        refresh_token: The refresh token from a previous OAuth flow

    Returns:
        dict: Token response containing new access_token and optionally refresh_token

    Raises:
        ValueError: If PAGERDUTY_CLIENT_SECRET environment variable is not set
        requests.HTTPError: If token refresh request fails
    """
    client_id = os.getenv("PAGERDUTY_CLIENT_ID", DEFAULT_CLIENT_ID)
    client_secret = os.getenv("PAGERDUTY_CLIENT_SECRET")

    if not client_secret:
        raise ValueError("PAGERDUTY_CLIENT_SECRET required for token refresh")

    response = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def _store_tokens(token_data):
    """Store OAuth tokens securely in OS keyring.

    Stores the access token, calculated expiry time, and optionally the refresh token
    if PAGERDUTY_CLIENT_SECRET is set (server mode).

    Args:
        token_data: Token response dict containing access_token, expires_in, and optionally refresh_token

    Returns:
        str: The access token that was stored

    Raises:
        PagerDutyAuthError: If keyring access fails
    """
    access_token = token_data["access_token"]
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEY_ACCESS_TOKEN, access_token)
    except Exception as e:
        raise PagerDutyAuthError(
            f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
        ) from e

    expiry = time.time() + token_data.get("expires_in", DEFAULT_TOKEN_EXPIRY_SECONDS)
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEY_TOKEN_EXPIRY, str(expiry))
    except Exception as e:
        raise PagerDutyAuthError(
            f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
        ) from e

    if "refresh_token" in token_data and os.getenv("PAGERDUTY_CLIENT_SECRET"):
        new_refresh = token_data.get("refresh_token")
        try:
            keyring.set_password(
                KEYRING_SERVICE, KEYRING_KEY_REFRESH_TOKEN, new_refresh
            )
        except Exception as e:
            raise PagerDutyAuthError(
                f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
            ) from e

    return access_token


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback redirect.

    Captures authorization code or error from PagerDuty OAuth redirect.
    Class attributes store the callback results for the OAuth flow.

    Attributes:
        code: Authorization code from successful OAuth callback
        error: Error message from failed OAuth callback
        expected_state: CSRF state token expected in the callback
    """

    code = None
    error = None
    expected_state = None

    def do_GET(self):
        """Handle GET request from OAuth callback redirect.

        Extracts authorization code or error from query parameters and displays
        appropriate success/failure message to the user.
        """
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        received_state = params.get("state", [None])[0]
        if received_state != CallbackHandler.expected_state:
            CallbackHandler.error = "state_mismatch"
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body>OAuth state mismatch. Possible CSRF attack. You can close this window.</body></html>"
            )
            return

        if "error" in params:
            CallbackHandler.error = params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = "<html><body>PagerDuty authorization failed. You can close this window.</body></html>"
            self.wfile.write(html.encode())
        elif "code" in params:
            CallbackHandler.code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = "<html><body>PagerDuty authorization successful! You can close this window.</body></html>"
            self.wfile.write(html.encode())
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body>Missing authorization code. You can close this window.</body></html>"
            )
            CallbackHandler.error = "missing_code"

    def log_message(self, format, *args):
        """Suppress HTTP server logging output.

        Override BaseHTTPRequestHandler's log_message to prevent
        verbose logging during OAuth callback.
        """
        return


def get_token():
    """Get or refresh OAuth access token for PagerDuty API.

    This function implements the complete OAuth flow with PKCE:
    1. Checks keyring for existing valid token
    2. Attempts token refresh if expired (requires PAGERDUTY_CLIENT_SECRET)
    3. Falls back to full OAuth authorization flow if needed

    The OAuth flow:
    - Opens browser for user authorization
    - Starts local HTTP server to receive callback
    - Exchanges authorization code for access token using PKCE
    - Stores tokens securely in OS keyring

    Returns:
        str: Valid OAuth access token

    Raises:
        PagerDutyAuthError: If keyring access fails
        Exception: If OAuth authorization fails or token exchange fails

    Environment Variables:
        PAGERDUTY_CLIENT_ID: OAuth client ID (optional, defaults to DEFAULT_CLIENT_ID)
        PAGERDUTY_CLIENT_SECRET: OAuth client secret (optional, enables token refresh)
    """
    try:
        token = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY_ACCESS_TOKEN)
    except Exception as e:
        raise PagerDutyAuthError(
            f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
        ) from e

    if token:
        try:
            expiry_str = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY_TOKEN_EXPIRY)
        except Exception as e:
            raise PagerDutyAuthError(
                f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
            ) from e

        if expiry_str:
            try:
                if time.time() < float(expiry_str):
                    return token
            except ValueError:
                logger.warning("Corrupt token expiry in keyring: %r", expiry_str)

        try:
            refresh_token = keyring.get_password(
                KEYRING_SERVICE, KEYRING_KEY_REFRESH_TOKEN
            )
        except Exception as e:
            raise PagerDutyAuthError(
                f"Keyring access failed: {e}. On headless Linux, install 'keyrings.alt' or set PAGERDUTY_API_TOKEN instead."
            ) from e

        client_secret = os.getenv("PAGERDUTY_CLIENT_SECRET")

        if refresh_token and client_secret:
            try:
                token_data = refresh_access_token(refresh_token)
                return _store_tokens(token_data)
            except requests.exceptions.HTTPError as e:
                if e.response is not None and 400 <= e.response.status_code < 500:
                    logger.warning(
                        f"Token refresh failed ({e.response.status_code}), clearing stored tokens"
                    )
                    safe_delete_password(KEYRING_SERVICE, KEYRING_KEY_ACCESS_TOKEN)
                    safe_delete_password(KEYRING_SERVICE, KEYRING_KEY_TOKEN_EXPIRY)
                    safe_delete_password(KEYRING_SERVICE, KEYRING_KEY_REFRESH_TOKEN)
                else:
                    logger.warning(f"Token refresh failed (server error): {e}")
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")
        else:
            safe_delete_password(KEYRING_SERVICE, KEYRING_KEY_ACCESS_TOKEN)
            safe_delete_password(KEYRING_SERVICE, KEYRING_KEY_TOKEN_EXPIRY)

    client_id = os.getenv("PAGERDUTY_CLIENT_ID", DEFAULT_CLIENT_ID)

    with _get_token_lock:
        CallbackHandler.code = None
        CallbackHandler.error = None
        CallbackHandler.expected_state = None

        state = secrets.token_urlsafe(32)
        CallbackHandler.expected_state = state

        verifier, challenge = generate_pkce_codes()

        server = HTTPServer(("localhost", OAUTH_CALLBACK_PORT), CallbackHandler)

        try:
            params = {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": OAUTH_REDIRECT_URI,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "scope": OAUTH_SCOPE,
                "state": state,
            }
            auth_url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}"

            webbrowser.open(auth_url)

            server.timeout = OAUTH_CALLBACK_TIMEOUT_SECONDS
            deadline = time.time() + OAUTH_TOTAL_TIMEOUT_SECONDS

            while CallbackHandler.code is None and CallbackHandler.error is None:
                if time.time() >= deadline:
                    raise PagerDutyAuthError("OAuth callback timed out after 5 minutes")
                server.handle_request()

            if CallbackHandler.error:
                raise Exception(f"OAuth authorization failed: {CallbackHandler.error}")

            response = requests.post(
                OAUTH_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": CallbackHandler.code,
                    "client_id": client_id,
                    "redirect_uri": OAUTH_REDIRECT_URI,
                    "code_verifier": verifier,
                },
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f"Token error: {response.text}")

            token_data = response.json()
            return _store_tokens(token_data)
        finally:
            server.server_close()


if __name__ == "__main__":
    token = get_token()
    if token and len(token) > 12:
        print(f"Token: {token[:8]}...{token[-4:]}")
    else:
        print("Token obtained successfully")
