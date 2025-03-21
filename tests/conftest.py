import json
import os
import pytest
from unittest.mock import patch, MagicMock

def pytest_configure(config):
    """Register custom test markers to make testing and iterating easier on the developer."""
    config.addinivalue_line("markers", "unit: Unit tests that do not require external dependencies")
    config.addinivalue_line("markers", "integration: Integration tests that require a real PagerDuty API key")
    config.addinivalue_line("markers", "client: Tests for the client sub-module")
    config.addinivalue_line("markers", "escalation_policies: Tests for the escalation_policies sub-module")
    config.addinivalue_line("markers", "incidents: Tests for the incidents sub-module")
    config.addinivalue_line("markers", "oncalls: Tests for the oncalls sub-module")
    config.addinivalue_line("markers", "schedules: Tests for the schedules sub-module")
    config.addinivalue_line("markers", "server: Tests for the server sub-module")
    config.addinivalue_line("markers", "services: Tests for the services sub-module")
    config.addinivalue_line("markers", "teams: Tests for the teams sub-module")
    config.addinivalue_line("markers", "users: Tests for the users sub-module")
    config.addinivalue_line("markers", "utils: Tests for the utils sub-module")
    config.addinivalue_line("markers", "parsers: Tests for the parsers sub-module")

skip_if_no_pagerduty_key = pytest.mark.skipif(
    not os.getenv("PAGERDUTY_API_KEY"),
    reason="Skipping test because PAGERDUTY_API_KEY is not set"
)

@pytest.fixture
def load_fixture():
    def _load_file(filename):
        with open(os.path.join('tests', 'fixtures', filename)) as f:
            return json.load(f)
    return _load_file

@pytest.fixture
def mock_get_api_client():
    """Mocks get_api_client and its list_all method."""
    with patch('pagerduty_mcp_server.client.get_api_client') as mock_get_api_client:
        mock_client = MagicMock()
        mock_get_api_client.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_escalation_policies(load_fixture):
    """Loads mock escalation policies from escalation_policies.json."""
    return load_fixture("escalation_policies_raw.json")

@pytest.fixture
def mock_escalation_policies_parsed(load_fixture):
    """Loads mock escalation policies from escalation_policies_parsed.json."""
    return load_fixture("escalation_policies_parsed.json")

@pytest.fixture
def mock_escalation_policy_ids(load_fixture):
    """Extracts expected escalation policy IDs from escalation_policies.json."""
    return [policy["id"] for policy in load_fixture("escalation_policies_raw.json")]

@pytest.fixture
def mock_incidents(load_fixture):
    """Loads mock incidents from incidents.json."""
    return load_fixture("incidents_raw.json")

@pytest.fixture
def mock_incidents_parsed(load_fixture):
    """Loads mock incidents from incidents.json."""
    return load_fixture("incidents_parsed.json")

@pytest.fixture
def mock_oncalls(load_fixture):
    """Loads mock oncalls from oncalls.json."""
    return load_fixture("oncalls_raw.json")

@pytest.fixture
def mock_oncalls_parsed(load_fixture):
    """Loads mock oncalls from oncalls_parsed.json."""
    return load_fixture("oncalls_parsed.json")

@pytest.fixture
def mock_schedules(load_fixture):
    """Loads mock schedules from schedules.json."""
    return load_fixture("schedules_raw.json")

@pytest.fixture
def mock_schedules_parsed(load_fixture):
    """Loads mock schedules from schedules_parsed.json."""
    return load_fixture("schedules_parsed.json")

@pytest.fixture
def mock_schedule_ids(load_fixture):
    """Extracts expected schedule IDs from schedules.json."""
    return [schedule["id"] for schedule in load_fixture("schedules_raw.json")]  

@pytest.fixture
def mock_services(load_fixture):
    """Loads mock services from services_raw.json."""
    return load_fixture("services_raw.json")

@pytest.fixture
def mock_services_parsed(load_fixture):
    """Loads mock services from services_parsed.json."""
    return load_fixture("services_parsed.json")

@pytest.fixture
def mock_service_ids(load_fixture):
    """Mocks service IDs expected based on team IDs in user.json."""
    return [service["id"] for service in load_fixture("services_raw.json")]

@pytest.fixture
def mock_teams(load_fixture):
    """Loads mock teams from teams_raw.json."""
    return load_fixture("teams_raw.json")

@pytest.fixture
def mock_teams_parsed(load_fixture):
    """Loads mock teams from teams_parsed.json."""
    return load_fixture("teams_parsed.json")

@pytest.fixture
def mock_team_ids(load_fixture):
    """Extracts expected team IDs from users_raw.json."""
    return [team["id"] for team in load_fixture("users_raw.json")["teams"]]

@pytest.fixture
def mock_user(load_fixture):
    """Loads a mock user from users_raw.json."""
    return load_fixture("users_raw.json")

@pytest.fixture
def mock_user_parsed(load_fixture):
    """Loads a mock user from users_parsed.json."""
    return load_fixture("users_parsed.json")
