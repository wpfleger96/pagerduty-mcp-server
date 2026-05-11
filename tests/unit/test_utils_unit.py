"""Unit tests for the utils module."""

import pytest

from pagerduty_mcp_server import utils


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_single_result():
    """Test that api_response_handler formats a single result correctly."""
    result = {"id": "123", "name": "test"}
    response = utils.api_response_handler(results=result, resource_name="test")

    assert response == {
        "metadata": {
            "count": 1,
            "description": "Found 1 result for resource type test",
        },
        "test": [result],
    }


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_multiple_results():
    """Test that api_response_handler formats multiple results correctly."""
    results = [{"id": "123", "name": "test1"}, {"id": "456", "name": "test2"}]
    response = utils.api_response_handler(results=results, resource_name="tests")

    assert response == {
        "metadata": {
            "count": 2,
            "description": "Found 2 results for resource type tests",
        },
        "tests": results,
    }


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_with_metadata():
    """Test that api_response_handler includes additional metadata."""
    result = {"id": "123", "name": "test"}
    additional_metadata = {"status": "active"}
    response = utils.api_response_handler(
        results=result, resource_name="test", additional_metadata=additional_metadata
    )

    assert response["metadata"]["status"] == "active"


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_char_limit_exceeded():
    """Test that api_response_handler returns soft error dict when character limit exceeded."""
    large_string = "x" * (utils.RESPONSE_CHAR_LIMIT + 1000)
    results = [{"data": large_string}]

    response = utils.api_response_handler(results=results, resource_name="tests")

    assert response["error"]["code"] == "LIMIT_EXCEEDED"
    assert f"{utils.RESPONSE_CHAR_LIMIT} characters" in response["error"]["message"]


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_byte_limit_exceeded():
    """Test that api_response_handler returns soft error dict when byte size limit exceeded."""
    binary_like_data = bytearray(range(255)) * (utils.RESPONSE_SIZE_LIMIT // 255 + 100)
    results = [{"data": str(binary_like_data)}]

    response = utils.api_response_handler(results=results, resource_name="tests")

    assert response["error"]["code"] == "LIMIT_EXCEEDED"
    assert f"{utils.RESPONSE_SIZE_LIMIT} bytes" in response["error"]["message"]


@pytest.mark.unit
@pytest.mark.utils
def test_api_response_handler_empty_resource_name():
    """Test that api_response_handler raises ValidationError for empty resource_name."""
    with pytest.raises(utils.ValidationError) as exc_info:
        utils.api_response_handler(results={"id": "123"}, resource_name="")
    assert str(exc_info.value) == "resource_name cannot be empty"


@pytest.mark.unit
@pytest.mark.utils
def test_validate_timestamp_range_valid_range():
    """Test that validate_timestamp_range accepts valid timestamp ranges."""
    since = "2024-01-01T00:00:00Z"
    until = "2024-03-01T00:00:00Z"

    # Should not raise any exception
    utils.validate_timestamp_range(since, until)


@pytest.mark.unit
@pytest.mark.utils
def test_validate_timestamp_range_since_after_until():
    """Test that validate_timestamp_range raises error when since is after until."""
    since = "2024-03-01T00:00:00Z"
    until = "2024-01-01T00:00:00Z"

    with pytest.raises(utils.ValidationError) as exc_info:
        utils.validate_timestamp_range(since, until)

    assert str(exc_info.value) == "`since` must be before `until`"


@pytest.mark.unit
@pytest.mark.utils
def test_validate_timestamp_range_exceeds_6_months():
    """Test that validate_timestamp_range raises error when range exceeds 6 months."""
    since = "2024-01-01T00:00:00Z"
    until = "2024-08-01T00:00:00Z"  # 7 months later

    with pytest.raises(utils.ValidationError) as exc_info:
        utils.validate_timestamp_range(since, until)

    assert (
        str(exc_info.value)
        == "The maximum query range is 6 months. Try narrowing your query range."
    )


@pytest.mark.unit
@pytest.mark.utils
def test_validate_timestamp_range_invalid_format():
    """Test that validate_timestamp_range propagates datetime parsing errors."""
    since = "invalid-date-format"
    until = "2024-03-01T00:00:00Z"

    with pytest.raises(ValueError):
        utils.validate_timestamp_range(since, until)
