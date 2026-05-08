"""Unit tests for the validation module."""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import validation
from pagerduty_mcp_server.models.incident import Incident
from pagerduty_mcp_server.models.schedule import Schedule
from pagerduty_mcp_server.models.user import User


@pytest.mark.unit
@pytest.mark.validation
class TestValidateIncludeFields:
    """Test the validate_include_fields function directly."""

    def test_valid_fields_user_model(self):
        """Test that valid User model fields pass validation."""
        valid_fields = ["id", "name", "email", "type", "description", "teams"]
        result = validation.validate_include_fields(valid_fields, User)
        assert result == valid_fields

    def test_valid_fields_incident_model(self):
        """Test that valid Incident model fields pass validation."""
        valid_fields = ["id", "title", "status", "urgency", "created_at"]
        result = validation.validate_include_fields(valid_fields, Incident)
        assert result == valid_fields

    def test_valid_fields_schedule_model(self):
        """Test that valid Schedule model fields pass validation."""
        valid_fields = ["id", "name", "time_zone", "description"]
        result = validation.validate_include_fields(valid_fields, Schedule)
        assert result == valid_fields

    def test_none_input(self):
        """Test that None input returns None."""
        result = validation.validate_include_fields(None, User)
        assert result is None

    def test_empty_list(self):
        """Test that empty list passes validation."""
        result = validation.validate_include_fields([], User)
        assert result == []

    def test_invalid_fields_raises_error(self):
        """Test that invalid fields raise ValueError with helpful message."""
        invalid_fields = ["invalid_field", "another_invalid"]

        with pytest.raises(ValueError) as exc_info:
            validation.validate_include_fields(invalid_fields, User)

        error_message = str(exc_info.value)
        assert (
            "Invalid include fields: ['another_invalid', 'invalid_field']"
            in error_message
        )
        assert "See `docs://tools` for more information" in error_message

    def test_mixed_valid_invalid_fields(self):
        """Test that mix of valid and invalid fields raises error for invalid ones."""
        mixed_fields = ["id", "name", "invalid_field", "email"]

        with pytest.raises(ValueError) as exc_info:
            validation.validate_include_fields(mixed_fields, User)

        error_message = str(exc_info.value)
        assert "Invalid include fields: ['invalid_field']" in error_message
        assert "Did you mean:" not in error_message  # No close matches for this field

    def test_close_match_suggestions(self):
        """Test that close matches provide helpful suggestions."""
        fields_with_typos = ["naem", "emial"]  # typos of "name", "email"

        with pytest.raises(ValueError) as exc_info:
            validation.validate_include_fields(fields_with_typos, User)

        error_message = str(exc_info.value)
        assert "Invalid include fields: ['emial', 'naem']" in error_message
        assert "Did you mean:" in error_message
        assert "'naem' ->" in error_message
        assert "'emial' ->" in error_message

    def test_case_sensitivity(self):
        """Test that field names are case sensitive."""
        case_wrong_fields = ["ID", "Name", "EMAIL"]  # Wrong case

        with pytest.raises(ValueError) as exc_info:
            validation.validate_include_fields(case_wrong_fields, User)

        error_message = str(exc_info.value)
        assert "Invalid include fields:" in error_message

    def test_excluded_fields_are_valid_for_include(self):
        """Test that fields marked as excluded=True in the model are still valid for include parameter."""
        # These fields exist in User model and are marked as exclude=True for serialization,
        # but they should still be valid for the include parameter since they're real model fields
        excluded_fields = ["time_zone", "color", "avatar_url", "billed"]

        # Should not raise an error - these are valid model fields
        result = validation.validate_include_fields(excluded_fields, User)
        assert result == excluded_fields

    def test_schema_generation_error_fallback(self):
        """Test that schema generation errors raise RuntimeError."""
        mock_model = MagicMock()
        mock_model.model_fields = {"id": MagicMock(), "name": MagicMock()}
        mock_model.model_json_schema.side_effect = Exception("Schema error")
        mock_model.__name__ = "MockModel"

        with pytest.raises(RuntimeError, match="Cannot determine valid fields"):
            validation.validate_include_fields(["id"], cast(Any, mock_model))

    def test_single_field(self):
        """Test validation with a single field."""
        result = validation.validate_include_fields(["id"], User)
        assert result == ["id"]

    def test_duplicate_fields(self):
        """Test validation with duplicate fields."""
        fields_with_dupes = ["id", "name", "id", "email"]
        result = validation.validate_include_fields(fields_with_dupes, User)
        assert result == fields_with_dupes  # Should preserve duplicates if all valid

    def test_extra_fields_accepted(self):
        """Test that extra_fields are accepted as valid include fields."""
        result = validation.validate_include_fields(
            ["notes", "past_incidents"],
            User,
            extra_fields=["notes", "past_incidents", "related_incidents"],
        )
        assert result == ["notes", "past_incidents"]

    def test_extra_fields_combined_with_model_fields(self):
        """Test that both model fields and extra_fields are accepted."""
        result = validation.validate_include_fields(
            ["id", "notes"], User, extra_fields=["notes"]
        )
        assert result == ["id", "notes"]

    def test_extra_fields_still_rejects_unknown(self):
        """Test that unknown fields are rejected even when extra_fields are provided."""
        with pytest.raises(ValueError, match="Invalid include fields"):
            validation.validate_include_fields(
                ["completely_invalid"], User, extra_fields=["notes"]
            )


@pytest.mark.unit
@pytest.mark.validation
class TestValidateIncludeParameterDecorator:
    """Test the validate_include_parameter decorator."""

    async def test_decorator_with_valid_include(self):
        """Test that decorator passes through valid include parameters."""

        @validation.validate_include_parameter(User)
        async def mock_function(include=None):
            return {"include": include}

        valid_fields = ["id", "name", "email"]
        result = await mock_function(include=valid_fields)
        assert result["include"] == valid_fields

    async def test_decorator_with_invalid_include(self):
        """Test that decorator raises error for invalid include parameters."""

        @validation.validate_include_parameter(User)
        async def mock_function(include=None):
            return {"include": include}

        invalid_fields = ["invalid_field"]

        with pytest.raises(ValueError) as exc_info:
            await mock_function(include=invalid_fields)

        assert "Invalid include fields:" in str(exc_info.value)

    async def test_decorator_with_none_include(self):
        """Test that decorator handles None include parameter."""

        @validation.validate_include_parameter(User)
        async def mock_function(include=None):
            return {"include": include}

        result = await mock_function(include=None)
        assert result["include"] is None

    async def test_decorator_without_include_parameter(self):
        """Test that decorator works when include parameter is not provided."""

        @validation.validate_include_parameter(User)
        async def mock_function(other_param=None):
            return {"other_param": other_param}

        result = await mock_function(other_param="test")
        assert result["other_param"] == "test"

    async def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""

        @validation.validate_include_parameter(User)
        async def mock_function(include=None):
            """This is a test function."""
            return {"include": include}

        assert mock_function.__name__ == "mock_function"
        assert mock_function.__doc__ == "This is a test function."

    async def test_decorator_with_args_and_kwargs(self):
        """Test that decorator works with positional args and keyword args."""

        @validation.validate_include_parameter(User)
        async def mock_function(arg1, arg2, include=None, other_kwarg=None):
            return {
                "arg1": arg1,
                "arg2": arg2,
                "include": include,
                "other_kwarg": other_kwarg,
            }

        valid_fields = ["id", "name"]
        result = await mock_function(
            "test1", "test2", include=valid_fields, other_kwarg="test3"
        )

        assert result["arg1"] == "test1"
        assert result["arg2"] == "test2"
        assert result["include"] == valid_fields
        assert result["other_kwarg"] == "test3"

    async def test_decorator_with_extra_fields(self):
        """Test that decorator passes extra_fields to validate_include_fields."""

        @validation.validate_include_parameter(User, extra_fields=["custom_field"])
        async def mock_function(include=None):
            return include

        result = await mock_function(include=["id", "custom_field"])
        assert result == ["id", "custom_field"]


@pytest.mark.unit
@pytest.mark.validation
class TestValidationIntegration:
    """Test validation integration with different model types."""

    def test_user_model_fields(self):
        """Test User model has expected fields available for validation."""
        user_fields = set(User.model_fields.keys())

        # Test some key fields that should be available
        expected_fields = {
            "id",
            "name",
            "email",
            "type",
            "description",
            "teams",
            "contact_methods",
            "notification_rules",
        }
        assert expected_fields.issubset(user_fields)

    def test_incident_model_fields(self):
        """Test Incident model has expected fields available for validation."""
        incident_fields = set(Incident.model_fields.keys())

        # Test some key fields that should be available
        expected_fields = {
            "id",
            "incident_number",
            "title",
            "status",
            "urgency",
            "created_at",
            "service",
        }
        assert expected_fields.issubset(incident_fields)

    def test_schedule_model_fields(self):
        """Test Schedule model has expected fields available for validation."""
        schedule_fields = set(Schedule.model_fields.keys())

        # Test some key fields that should be available
        expected_fields = {
            "id",
            "name",
            "time_zone",
            "description",
            "teams",
            "escalation_policies",
        }
        assert expected_fields.issubset(schedule_fields)

    def test_excluded_fields_are_still_valid_model_fields(self):
        """Test that excluded fields are still considered valid for include parameter."""
        # User model has several excluded fields, but they're still valid model fields
        excluded_fields = ["time_zone", "color", "avatar_url", "billed", "role"]

        for field in excluded_fields:
            # Should not raise an error - these are valid model fields
            result = validation.validate_include_fields([field], User)
            assert result == [field]
