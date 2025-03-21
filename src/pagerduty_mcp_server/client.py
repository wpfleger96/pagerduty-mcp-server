import os
import sys
import logging
import pagerduty
from importlib.metadata import version

logger = logging.getLogger(__name__)

def get_api_client():
    """Get a configured PagerDuty API client.

    Returns:
        RestApiV2Client: A configured PagerDuty API client
        
    Raises:
        SystemExit: If PAGERDUTY_API_KEY environment variable is not set
    """

    try:
        api_key = os.environ['PAGERDUTY_API_KEY']
    except KeyError:
        logger.error("PAGERDUTY_API_KEY not found in environment variables.")
        sys.exit(1)

    client = pagerduty.RestApiV2Client(api_key)
    client.headers['User-Agent'] = f'pagerduty-mcp-server/{version("pagerduty_mcp_server")}'
    return client
