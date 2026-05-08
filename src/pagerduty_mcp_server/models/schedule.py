"""Pydantic models for PagerDuty Schedules."""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from .common import PagerDutyBaseModel, Reference


class ScheduleLayerUser(PagerDutyBaseModel):
    """A user in a schedule layer."""

    id: str
    summary: Optional[str] = None


class ScheduleLayer(PagerDutyBaseModel):
    """A schedule layer."""

    # Required field - always present
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None

    # Collections - present but can be empty
    users: List[ScheduleLayerUser] = []

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
    name: Optional[str] = None
    summary: Optional[str] = None
    time_zone: Optional[str] = None

    # Optional fields - can be None in API responses
    description: Optional[str] = None

    # Collections - present but can be empty
    escalation_policies: List[Reference] = []
    teams: List[Reference] = []
    schedule_layers: List[ScheduleLayer] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: Always 'schedule'"
    )
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    http_cal_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: HTTP calendar URL"
    )
    final_schedule: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Final schedule configuration"
    )
    overrides_subschedule: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Override subschedule configuration"
    )
