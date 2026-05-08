"""Pydantic models for PagerDuty Services."""

from typing import List, Optional

from pydantic import Field

from .common import PagerDutyBaseModel, Reference


class Service(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Service.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Optional fields - can be None in API responses
    description: Optional[str] = None

    # Collections - present but can be empty
    teams: List[Reference] = []
    integrations: List[Reference] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
