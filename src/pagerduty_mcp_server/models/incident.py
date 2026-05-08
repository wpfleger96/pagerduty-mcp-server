"""Pydantic models for PagerDuty Incidents."""

from typing import Any, Dict, List, Optional

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
    incident_number: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    urgency: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    last_status_change_at: Optional[str] = None

    # Optional fields - can be None in API responses
    resolved_at: Optional[str] = None
    alert_counts: Optional[Dict[str, Any]] = None
    body_details: Optional[Dict[str, Any]] = None
    client_url: Optional[str] = None

    # References - can be None
    service: Optional[IdOnly] = None
    escalation_policy: Optional[Reference] = None
    last_status_change_by: Optional[Reference] = None

    # Collections - present but can be empty
    assignments: List[AssignmentItem] = []
    acknowledgements: List[AcknowledgementItem] = []
    teams: List[Reference] = []

    # Raw body field for processing
    body: Optional[Dict[str, Any]] = None

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: Always 'incident'"
    )
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    incident_key: Optional[str] = Field(
        None, exclude=True, description="Excluded: External incident key"
    )
    assigned_via: Optional[str] = Field(
        None, exclude=True, description="Excluded: How incident was assigned"
    )
    incident_type: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Incident type metadata"
    )
    is_mergeable: Optional[bool] = Field(
        None, exclude=True, description="Excluded: Whether incident can be merged"
    )
    pending_actions: Optional[List[Dict[str, Any]]] = Field(
        None, exclude=True, description="Excluded: Pending actions list"
    )
    priority: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Priority metadata"
    )
    resolve_reason: Optional[str] = Field(
        None, exclude=True, description="Excluded: Reason for resolution"
    )
    responder_requests: Optional[List[Dict[str, Any]]] = Field(
        None, exclude=True, description="Excluded: Responder requests list"
    )
    subscriber_requests: Optional[List[Dict[str, Any]]] = Field(
        None, exclude=True, description="Excluded: Subscriber requests list"
    )
    alert_grouping: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Alert grouping configuration"
    )
    basic_alert_grouping: Optional[Dict[str, Any]] = Field(
        None, exclude=True, description="Excluded: Basic alert grouping configuration"
    )
    incidents_responders: Optional[List[Dict[str, Any]]] = Field(
        None, exclude=True, description="Excluded: Incident responders list"
    )
    first_trigger_log_entry: Optional[Dict[str, Any]] = Field(
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
                        k for k in raw_body_details.keys() if k != "title"
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
