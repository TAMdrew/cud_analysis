"""Tests for the Configuration Manager."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from finops_analysis_platform.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test suite for the ConfigManager."""

    def setUp(self):
        """Set up temporary config files for tests."""
        self.test_yaml_path = Path("test_config.yaml")
        self.test_env_path = Path(".test.env")
        with open(self.test_yaml_path, "w") as f:
            f.write(
                """
gcp:
  project_id: yaml-project
  location: us-central1
analysis:
  risk_tolerance: medium
"""
            )
        with open(self.test_env_path, "w") as f:
            f.write("GCP_LOCATION=env-location\nANALYSIS_RISK_TOLERANCE=high")

    def tearDown(self):
        """Clean up temporary files."""
        if self.test_yaml_path.exists():
            self.test_yaml_path.unlink()
        if self.test_env_path.exists():
            self.test_env_path.unlink()

    def test_load_from_yaml(self):
        """Test loading configuration from a YAML file."""
        cm = ConfigManager(config_path=str(self.test_yaml_path), env_path=None)
        self.assertEqual(cm.get("gcp.project_id"), "yaml-project")
        self.assertEqual(cm.get("analysis.risk_tolerance"), "medium")

    def test_override_with_env_file(self):
        """Test that .env file values override YAML values."""
        cm = ConfigManager(
            config_path=str(self.test_yaml_path), env_path=str(self.test_env_path)
        )
        self.assertEqual(cm.get("gcp.location"), "env-location")
        self.assertEqual(cm.get("analysis.risk_tolerance"), "high")

    @patch.dict(os.environ, {"GCP_PROJECT_ID": "os-project"})
    def test_override_with_os_env(self):
        """Test that OS environment variables override all other sources."""
        cm = ConfigManager(
            config_path=str(self.test_yaml_path), env_path=str(self.test_env_path)
        )
        self.assertEqual(cm.get("gcp.project_id"), "os-project")

    def test_get_with_default_value(self):
        """Test the get method with a default value for a missing key."""
        cm = ConfigManager(config_path=str(self.test_yaml_path), env_path=None)
        self.assertEqual(cm.get("gcp.nonexistent_key", "default"), "default")


if __name__ == "__main__":
    unittest.main()
