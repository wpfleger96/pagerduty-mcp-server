from typing import Dict, List, Optional, Union
from datetime import datetime
import re
from dataclasses import dataclass, field

@dataclass
class ProcessedIncident:
    """
    Data class to represent a fully processed PagerDuty incident.
    """

    number: int
    title: str
    status: str
    urgency: str
    created_at: str
    resolved_at: Optional[str]
    assignee: Optional[str]
    acknowledged_by: Optional[str]
    service: str
    teams: List[str] = field(default_factory=list)
    auto_resolved: bool = False

    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'title': self.title,
            'status': self.status,
            'urgency': self.urgency,
            'created_at': self.created_at,
            'resolved_at': self.resolved_at,
            'assignee': self.assignee,
            'acknowledged_by': self.acknowledged_by,
            'service': self.service,
            'teams': self.teams,
            'auto_resolved': self.auto_resolved
        }


def process_incident(raw: Dict) -> Dict:
    """Convert raw PagerDuty incident to simplified format to reduce number of LLM tokens used"""

    assignments = raw.get('assignments') or []
    assignee = assignments[0].get('assignee', {}).get('summary') if assignments else None

    acknowledgements = raw.get('acknowledgements') or []
    acknowledged_by = acknowledgements[0].get('acknowledger', {}).get('summary') if acknowledgements else None

    auto_resolved = (
        raw['status'] == 'resolved' and 
        raw.get('last_status_change_by', {}).get('type') == 'service_reference'
    )


    inc = ProcessedIncident(
        number=raw['incident_number'],
        title=raw['title'],
        status=raw['status'],
        urgency=raw['urgency'],
        created_at=raw['created_at'],
        resolved_at=raw.get('resolved_at'),
        assignee=assignee,
        acknowledged_by=acknowledged_by,
        service=raw.get('service', {}).get('summary'),
        teams=[t.get('summary') for t in raw.get('teams', [])],
        auto_resolved=auto_resolved
    )

    return inc.to_dict()


def process_incidents(incidents: Union[Dict, List[Dict]]) -> Dict:
    """Process a single incident (dict) or a list of incidents (list of dicts) and generate summary"""

    if isinstance(incidents, dict):
        incidents = [incidents]

    processed = [process_incident(i) for i in incidents]
    
    total = len(processed)
    auto_resolved = sum(1 for i in processed if i.get('auto_resolved'))
    
    return {
        'total': total,
        'auto_resolved': auto_resolved,
        'auto_resolved_pct': round((auto_resolved / total * 100) if total else 0, 1),
        'by_status': _count_field(processed, 'status'),
        'by_urgency': _count_field(processed, 'urgency'),
        'by_service': _count_field(processed, 'service'),
        'by_team': _count_field(processed, 'teams', flatten=True),
        'incidents': processed
    }


def _count_field(items: List[Dict], field: str, flatten: bool = False) -> Dict:
    """Count occurrences of field values in a list of dicts"""

    values = []
    for item in items:
        if flatten and isinstance(item.get(field), list):
            values.extend(item[field])
        else:
            values.append(item.get(field))
    return {k: v for k, v in sorted(
        {val: values.count(val) for val in set(values) if val}.items()
    )}
