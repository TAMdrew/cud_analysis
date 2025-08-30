"""Manages loading and accessing configuration for the application.

This module provides a ConfigManager class that loads configuration from a
YAML file and allows for overrides from environment variables, providing a
flexible and robust way to configure the application.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Set up a logger for this module
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages loading and accessing of application configuration.

    This class loads settings from a YAML file and merges them with settings
    from a .env file and environment variables, with environment variables
    taking the highest precedence.

    Attributes:
        config: A dictionary holding the final, merged configuration.
    """

    def __init__(
        self, config_path: str = "config.yaml", env_path: Optional[str] = ".env"
    ):
        """Initializes the ConfigManager and loads configuration.

        Args:
            config_path: The path to the YAML configuration file.
            env_path: The path to the .env file. If None, the .env file is not
                loaded.
        """
        self.config_path = Path(config_path)
        self.env_path = Path(env_path) if env_path else None
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Loads configuration from YAML and overrides with environment variables."""
        if self.env_path and self.env_path.is_file():
            load_dotenv(dotenv_path=self.env_path)
            logger.info("Loaded environment variables from %s", self.env_path)

        if self.config_path.is_file():
            with open(self.config_path, "r", encoding="utf-8") as file_handle:
                self.config = yaml.safe_load(file_handle)
                logger.info("Loaded configuration from %s", self.config_path)
        elif self.config_path != Path("config.yaml"):  # Only warn if non-default path
            logger.error(
                "Config file not found at specified path: %s",
                self.config_path,
            )
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        else:
            logger.info(
                "Default config file not found. Using environment variables only."
            )
            self.config = self._get_default_config()

        self._override_with_env_vars(self.config)
        self._infer_gcp_project()

    def _infer_gcp_project(self):
        """Infers GCP project ID from standard env vars if not set."""
        gcp_config = self.config.setdefault("gcp", {})
        if "project_id" not in gcp_config or not gcp_config["project_id"]:
            project_id = os.getenv("GCP_PROJECT_ID") or os.getenv(
                "GOOGLE_CLOUD_PROJECT"
            )
            if project_id:
                gcp_config["project_id"] = project_id
                logger.info(
                    "Inferred GCP Project ID ('%s') from environment variables.",
                    project_id,
                )

    def _get_default_config(self) -> Dict[str, Any]:
        """Returns a minimal default configuration."""
        return {
            "gcp": {"location": "us-central1"},
            "analysis": {"risk_tolerance": "medium"},
            "cud_strategy": {"base_layer_coverage": 40},
        }

    def _override_with_env_vars(self, config_dict: Dict[str, Any], prefix: str = ""):
        """Recursively overrides dictionary values with environment variables.

        Example: A config {'gcp': {'project_id': 'x'}} will look for an
        environment variable named GCP_PROJECT_ID.

        Args:
            config_dict: The dictionary to override.
            prefix: The prefix to use for constructing the env var name.
        """
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self._override_with_env_vars(value, prefix=f"{prefix}{key}_")
            else:
                env_var_name = (prefix + key).upper()
                env_value = os.getenv(env_var_name)
                if env_value is not None:
                    # Attempt to cast the environment variable to the original type
                    original_value = config_dict[key]
                    try:
                        if original_value is None:
                            config_dict[key] = env_value
                        elif isinstance(original_value, bool):
                            config_dict[key] = env_value.lower() in (
                                "true",
                                "1",
                                "t",
                                "yes",
                            )
                        elif isinstance(original_value, int):
                            config_dict[key] = int(env_value)
                        elif isinstance(original_value, float):
                            config_dict[key] = float(env_value)
                        else:  # Treat as string by default
                            config_dict[key] = env_value

                        logger.info(
                            "Overriding config '%s' with value from env var '%s'.",
                            prefix + key,
                            env_var_name,
                        )
                    except (ValueError, TypeError):
                        config_dict[key] = env_value
                        logger.warning(
                            "Could not cast env var '%s' to type of '%s'. Using string.",
                            env_var_name,
                            key,
                        )

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration value using dot notation for nested keys.

        Args:
            key: The configuration key to retrieve (e.g., 'gcp.project_id').
            default: The default value to return if the key is not found.

        Returns:
            The requested configuration value or the default.
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def __getitem__(self, key: str) -> Any:
        """Gets a configuration value using dictionary-style access.

        Note:
            This method does not support dot notation for nested keys.

        Args:
            key: The top-level configuration key to retrieve.

        Returns:
            The requested configuration value.

        Raises:
            KeyError: If the key is not found in the configuration.
        """
        return self.config[key]

    def __repr__(self) -> str:
        """Returns a string representation of the ConfigManager instance."""
        return f"ConfigManager(config_path='{self.config_path}')"
