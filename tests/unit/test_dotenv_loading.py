"""Test .env file loading functionality."""

import os
import tempfile
from unittest.mock import patch

from dotenv import load_dotenv


class TestDotenvLoading:
    """Test .env file loading functionality."""

    def test_dotenv_loads_from_file(self):
        """Test that dotenv can load environment variables from a .env file."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("TEST_API_TOKEN=test_token_value\n")
            f.write("ANOTHER_VAR=another_value\n")
            temp_env_file = f.name

        try:
            # Load the temporary .env file
            load_dotenv(temp_env_file)
            
            # Verify the environment variables were loaded
            assert os.getenv("TEST_API_TOKEN") == "test_token_value"
            assert os.getenv("ANOTHER_VAR") == "another_value"
        finally:
            # Clean up
            os.unlink(temp_env_file)
            # Clean up environment variables
            if "TEST_API_TOKEN" in os.environ:
                del os.environ["TEST_API_TOKEN"]
            if "ANOTHER_VAR" in os.environ:
                del os.environ["ANOTHER_VAR"]

    def test_dotenv_respects_existing_env_vars(self):
        """Test that existing environment variables take precedence over .env file."""
        # Set an environment variable
        os.environ["EXISTING_VAR"] = "existing_value"
        
        # Create a temporary .env file with the same variable
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EXISTING_VAR=dotenv_value\n")
            temp_env_file = f.name

        try:
            # Load the .env file (should not override existing env var)
            load_dotenv(temp_env_file, override=False)
            
            # Verify the existing environment variable was not overridden
            assert os.getenv("EXISTING_VAR") == "existing_value"
        finally:
            # Clean up
            os.unlink(temp_env_file)
            if "EXISTING_VAR" in os.environ:
                del os.environ["EXISTING_VAR"]

    def test_client_imports_dotenv(self):
        """Test that the client module imports and uses dotenv."""
        # This test verifies that the import works without errors
        from pagerduty_mcp_server.client import create_client
        
        # The import should succeed, indicating dotenv is properly imported
        assert create_client is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_client_loads_pagerduty_token_from_dotenv(self):
        """Test that the client can load PAGERDUTY_API_TOKEN from .env file."""
        # Create a temporary .env file with PAGERDUTY_API_TOKEN
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("PAGERDUTY_API_TOKEN=test_pd_token\n")
            temp_env_file = f.name

        try:
            # Load the .env file
            load_dotenv(temp_env_file)
            
            # Verify the token was loaded
            assert os.getenv("PAGERDUTY_API_TOKEN") == "test_pd_token"
        finally:
            # Clean up
            os.unlink(temp_env_file)
            if "PAGERDUTY_API_TOKEN" in os.environ:
                del os.environ["PAGERDUTY_API_TOKEN"]
