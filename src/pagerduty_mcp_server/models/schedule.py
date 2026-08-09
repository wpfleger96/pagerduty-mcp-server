"""Pydantic models for PagerDuty Schedules."""

from typing import Any

from pydantic import Field, field_validator

from .common import PagerDutyBaseModel, Reference


class ScheduleLayerUser(PagerDutyBaseModel):
    """A user in a schedule layer."""

    id: str
    summary: str | None = None


class ScheduleLayer(PagerDutyBaseModel):
    """A schedule layer."""

    # Required field - always present
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: str | None = None
    start: str | None = None
    end: str | None = None

    # Collections - present but can be empty
    users: list[ScheduleLayerUser] = []

    @field_validator("users", mode="before")
    @classmethod
    def transform_users(cls, v):
        """Transform users from nested structure to flat structure."""
        if not isinstance(v, list):
            return v

        transformed_users = []
        for user_entry in v:
            if isinstance(user_entry, dict):
                # Handle nested structure: {"user": {"id": "...", "summary": "..."}}
                if "user" in user_entry:
                    user_data = user_entry["user"]
                    if user_data.get("id"):
                        transformed_user = {"id": user_data["id"]}
                        if user_data.get("summary"):
                            transformed_user["summary"] = user_data["summary"]
                        transformed_users.append(transformed_user)
                # Handle flat structure: {"id": "...", "summary": "..."}
                elif user_entry.get("id"):
                    transformed_users.append(user_entry)

        return transformed_users


class Schedule(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Schedule.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: str | None = None
    summary: str | None = None
    time_zone: str | None = None

    # Optional fields - can be None in API responses
    description: str | None = None

    # Collections - present but can be empty
    escalation_policies: list[Reference] = []
    teams: list[Reference] = []
    schedule_layers: list[ScheduleLayer] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: str | None = Field(
        None, exclude=True, description="Excluded: Always 'schedule'"
    )
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")
    self: str | None = Field(None, exclude=True, description="Excluded: API URL")
    http_cal_url: str | None = Field(
        None, exclude=True, description="Excluded: HTTP calendar URL"
    )
    final_schedule: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Final schedule configuration"
    )
    overrides_subschedule: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Override subschedule configuration"
    )
