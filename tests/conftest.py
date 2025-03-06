import json
import os
import pagerduty
import pytest

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
