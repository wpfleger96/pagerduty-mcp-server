"""Unit tests for async_utils module."""

import threading
from unittest.mock import MagicMock

import pytest
from pagerduty_mcp_server.async_utils import paginate, safe_execute_async


@pytest.mark.unit
@pytest.mark.asyncio
async def test_safe_execute_async_success():
    """Test successful async execution."""
    mock_func = MagicMock(return_value="test_result")
    result = await safe_execute_async(mock_func, "test operation")
    assert result == "test_result"
    mock_func.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_safe_execute_async_exception():
    """Test exception handling in async execution."""
    mock_func = MagicMock(side_effect=RuntimeError("API Error"))
    with pytest.raises(RuntimeError) as exc_info:
        await safe_execute_async(mock_func, "test operation")
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_safe_execute_async_runs_in_thread():
    """Test that function runs in a different thread from the main thread."""
    main_thread_id = threading.current_thread().ident

    def get_thread_id():
        return threading.current_thread().ident

    result_thread_id = await safe_execute_async(get_thread_id, "thread test")
    assert result_thread_id != main_thread_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_caps_at_max_records():
    """paginate must stop iterating once max_records items have been collected."""
    mock_client = MagicMock()
    items = [{"id": f"P{i}"} for i in range(50)]
    # Track how many items get pulled from the iterator. iter_all returns a
    # generator; if paginate iterates the full thing, count will reach 50.
    consumed = {"count": 0}

    def fake_iter(*_args, **_kwargs):
        for item in items:
            consumed["count"] += 1
            yield item

    mock_client.iter_all.side_effect = fake_iter

    results = await paginate(
        mock_client,
        "/teams",
        params={},
        max_records=3,
        operation_name="test",
    )

    assert len(results) == 3
    assert results == items[:3]
    # Critical: paginate must short-circuit. We allow off-by-one (the generator
    # may have produced item #4 but paginate broke before appending it), so
    # cap the strict upper bound at max_records + 1.
    assert consumed["count"] <= 4, (
        f"paginate consumed {consumed['count']} items but should have stopped near 3"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_returns_partial_when_iterator_exhausted():
    """If the iterator runs out before max_records is reached, return what we got."""
    mock_client = MagicMock()
    mock_client.iter_all.return_value = iter([{"id": "P1"}, {"id": "P2"}])

    results = await paginate(
        mock_client,
        "/teams",
        params={},
        max_records=100,
        operation_name="test",
    )

    assert results == [{"id": "P1"}, {"id": "P2"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_rejects_limit_in_params():
    """Defensive guard: a stray `limit` in params would cause SDK page-size
    misuse and re-introduce the bug paginate exists to prevent."""
    mock_client = MagicMock()

    with pytest.raises(ValueError, match="must not contain 'limit'"):
        await paginate(
            mock_client,
            "/teams",
            params={"limit": 2},
            max_records=10,
            operation_name="test",
        )

    # Must short-circuit *before* hitting the API.
    mock_client.iter_all.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_empty_iterator():
    """paginate returns empty list when iter_all yields nothing."""
    mock_client = MagicMock()
    mock_client.iter_all.return_value = iter([])

    results = await paginate(
        mock_client, "/teams", params={}, max_records=10, operation_name="test empty"
    )
    assert results == []
    mock_client.iter_all.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_api_error_mid_iteration():
    """paginate propagates errors raised by iter_all mid-iteration."""
    mock_client = MagicMock()

    def failing_iter(*_args, **_kwargs):
        yield {"id": "P1"}
        raise RuntimeError("Mid-pagination API error")

    mock_client.iter_all.side_effect = failing_iter

    with pytest.raises(RuntimeError, match="Mid-pagination API error"):
        await paginate(
            mock_client,
            "/teams",
            params={},
            max_records=10,
            operation_name="test error",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_uses_optimal_page_size():
    """paginate passes min(max_records, 100) as page_size to iter_all."""
    mock_client = MagicMock()
    mock_client.iter_all.return_value = iter([{"id": "P1"}, {"id": "P2"}])

    await paginate(
        mock_client,
        "/teams",
        params={"key": "val"},
        max_records=5,
        operation_name="test page size",
    )
    mock_client.iter_all.assert_called_once_with(
        "/teams", params={"key": "val"}, page_size=5
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_paginate_page_size_caps_at_100():
    """paginate caps page_size at 100 even for large max_records."""
    mock_client = MagicMock()
    mock_client.iter_all.return_value = iter([{"id": f"P{i}"} for i in range(100)])

    await paginate(
        mock_client, "/teams", params={}, max_records=500, operation_name="test cap"
    )
    mock_client.iter_all.assert_called_once_with("/teams", params={}, page_size=100)
