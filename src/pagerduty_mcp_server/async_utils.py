"""Utilities for async operations with synchronous PagerDuty client."""

import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


# Default cap when a list tool is called without an explicit `limit`.
# Each list tool's docstring exposes `limit` to the caller; this default keeps
# response sizes reasonable when no limit is provided. The PagerDuty API returns
# 100 results per page by default, so 100 also avoids extra HTTP round-trips in
# the common case.
DEFAULT_MAX_RESULTS = 100


async def safe_execute_async(func: Callable[[], Any], operation_name: str) -> Any:
    """Execute a synchronous function asynchronously in a thread pool.

    This wrapper allows synchronous PagerDuty API calls to be executed
    without blocking the event loop, using asyncio.to_thread.

    Args:
        func: A callable that performs the synchronous operation
        operation_name: A descriptive name for the operation (used in error messages)

    Returns:
        The result of the synchronous operation

    Raises:
        Exception: Re-raises any exception from the operation with context
    """
    try:
        return await asyncio.to_thread(func)
    except Exception as e:
        logger.error(f"Failed to execute {operation_name}: {e}")
        raise


async def paginate(
    pd_client: Any,
    entity: str,
    params: Dict[str, Any],
    *,
    max_records: int,
    operation_name: str,
) -> List[Dict[str, Any]]:
    """Iterate a PagerDuty list endpoint, stopping after `max_records` items.

    This is the canonical pattern for capping list results from the
    `pagerduty` SDK — the `pd_client.list_all(...)` method paginates through
    *every* page regardless of any cap, and any `limit` key inside `params`
    is interpreted by the SDK as the per-page size (NOT a total cap), which
    causes excessive HTTP requests when small values are passed.

    Use this helper instead of `list_all` for any list tool that exposes a
    `limit` parameter to callers.

    IMPORTANT: Do NOT include `limit` in `params`. Let the SDK default the
    per-page size (100). Pass the user-supplied limit via `max_records` so
    iteration stops as soon as enough results are collected.

    Args:
        pd_client: The PagerDuty REST API client (pagerduty.RestApiV2Client)
        entity: The endpoint path (e.g. "/teams", "/users")
        params: Query parameters for the request (must NOT contain a `limit` key)
        max_records: Hard cap on the number of records returned
        operation_name: Descriptive name for error logging

    Returns:
        A list of result dicts, capped at `max_records` items.
    """
    if "limit" in params:
        # Defensive: a stray `limit` would force the SDK to use it as page_size
        # and re-introduce the bug this helper is designed to avoid.
        raise ValueError(
            "paginate() params must not contain 'limit'; use max_records to cap results."
        )

    def _collect() -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        optimal_page_size = min(max_records, 100)
        for item in pd_client.iter_all(
            entity, params=params, page_size=optimal_page_size
        ):
            results.append(item)
            if len(results) >= max_records:
                break
        return results

    return await safe_execute_async(_collect, operation_name)
