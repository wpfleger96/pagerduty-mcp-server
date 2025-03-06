import os
import sys
import logging
import pagerduty

logger = logging.getLogger("pagerduty-mcp-server")

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
    return pagerduty.RestApiV2Client(api_key)
