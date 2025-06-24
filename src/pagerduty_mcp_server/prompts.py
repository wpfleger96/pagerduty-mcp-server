"""Custom prompts for the PagerDuty MCP Server."""

import logging

from mcp.server.fastmcp.prompts import base

logger = logging.getLogger(__name__)


def handle_large_results(
    *, resource_name: str, limits_exceeded: str
) -> base.AssistantMessage:
    """Guidance for handling large result sets from PagerDuty API."""

    return base.AssistantMessage(
        f"""
IMPORTANT: The query for {resource_name} exceeded response size limits of {limits_exceeded}. This must be addressed to prevent context window exhaustion.

REQUIRED ACTION: You must modify your query to return fewer results. Here are the specific steps you should take:

1. FILTER THE RESULTS:
   - Add time range filters (since/until) to query smaller time periods
   - Add status filters (triggered, acknowledged, resolved)
   - Filter by specific teams or services
   - Use the 'limit' parameter to request fewer results

2. IMPLEMENT CHUNKING:
   - Break the query into smaller time periods
   - For example, if querying a month of incidents:
     * Query one week at a time
     * Combine the results programmatically
   - For user lists, filter by team or role

3. FOLLOW BEST PRACTICES:
   - Always use the most specific filters available
   - Cache results to avoid repeated large queries
   - Process results in smaller batches

CRITICAL: The API limit exists to ensure system performance and reliability. You must implement one or more of these solutions before proceeding. Breaking queries into smaller chunks is more efficient than attempting to process all results at once.
"""
    )
