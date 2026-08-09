"""Pydantic models for PagerDuty Incidents."""

from typing import Any

from pydantic import Field, model_validator

from .common import IdOnly, PagerDutyBaseModel, Reference


class AssignmentItem(PagerDutyBaseModel):
    """An assignment in an incident."""

    assignee: Reference
    at: str


class AcknowledgementItem(PagerDutyBaseModel):
    """An acknowledgement in an incident."""

    acknowledger: Reference
    at: str


class Incident(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Incident.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    incident_number: int | None = None
    title: str | None = None
    status: str | None = None
    urgency: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    summary: str | None = None
    description: str | None = None
    last_status_change_at: str | None = None

    # Optional fields - can be None in API responses
    resolved_at: str | None = None
    alert_counts: dict[str, Any] | None = None
    body_details: dict[str, Any] | None = None
    client_url: str | None = None

    # References - can be None
    service: IdOnly | None = None
    escalation_policy: Reference | None = None
    last_status_change_by: Reference | None = None

    # Collections - present but can be empty
    assignments: list[AssignmentItem] = []
    acknowledgements: list[AcknowledgementItem] = []
    teams: list[Reference] = []

    # Raw body field for processing
    body: dict[str, Any] | None = None

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: str | None = Field(
        None, exclude=True, description="Excluded: Always 'incident'"
    )
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")
    self: str | None = Field(None, exclude=True, description="Excluded: API URL")
    incident_key: str | None = Field(
        None, exclude=True, description="Excluded: External incident key"
    )
    assigned_via: str | None = Field(
        None, exclude=True, description="Excluded: How incident was assigned"
    )
    incident_type: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Incident type metadata"
    )
    is_mergeable: bool | None = Field(
        None, exclude=True, description="Excluded: Whether incident can be merged"
    )
    pending_actions: list[dict[str, Any]] | None = Field(
        None, exclude=True, description="Excluded: Pending actions list"
    )
    priority: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Priority metadata"
    )
    resolve_reason: str | None = Field(
        None, exclude=True, description="Excluded: Reason for resolution"
    )
    responder_requests: list[dict[str, Any]] | None = Field(
        None, exclude=True, description="Excluded: Responder requests list"
    )
    subscriber_requests: list[dict[str, Any]] | None = Field(
        None, exclude=True, description="Excluded: Subscriber requests list"
    )
    alert_grouping: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Alert grouping configuration"
    )
    basic_alert_grouping: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: Basic alert grouping configuration"
    )
    incidents_responders: list[dict[str, Any]] | None = Field(
        None, exclude=True, description="Excluded: Incident responders list"
    )
    first_trigger_log_entry: dict[str, Any] | None = Field(
        None, exclude=True, description="Excluded: First trigger log entry reference"
    )

    @model_validator(mode="after")
    def extract_body_details(self):
        """Extract body_details from the nested body structure."""
        if self.body and not self.body_details:
            body_payload = self.body.get("details", {}).get("__pd_cef_payload")
            if isinstance(body_payload, dict):
                if body_payload.get("client_url") is not None:
                    self.client_url = body_payload["client_url"]

                raw_body_details = body_payload.get("details")
                if isinstance(raw_body_details, dict) and raw_body_details:
                    # Get all keys except 'title'
                    keys_for_body_details = [
                        k for k in raw_body_details if k != "title"
                    ]

                    # Extract only the specified keys
                    parsed_body_details = {}
                    for key in keys_for_body_details:
                        value = raw_body_details.get(key)
                        if value is not None:
                            parsed_body_details[key] = value

                    if parsed_body_details:
                        self.body_details = parsed_body_details

        # Remove the raw body field from output
        self.body = None
        return self
