import os
import yaml
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, Optional

# Set up a logger for this module
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    A robust class to manage configuration for the FinOps analysis platform.
    It loads from a YAML file and allows overrides from environment variables.
    """

    def __init__(self, config_path: str = 'config.yaml', env_path: Optional[str] = '.env'):
        """
        Initialize the ConfigManager.

        Args:
            config_path: The path to the YAML configuration file.
            env_path: The path to the .env file. If None, .env file is not loaded.
        """
        self.config_path = Path(config_path)
        self.env_path = Path(env_path) if env_path else None
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """
        Load the configuration from the YAML file and override with environment variables.
        """
        # Load environment variables from .env file if it exists
        if self.env_path and self.env_path.is_file():
            load_dotenv(dotenv_path=self.env_path)
            logger.info(f"Loaded environment variables from {self.env_path}")

        # Load base configuration from YAML file
        if self.config_path.is_file():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
        else:
            logger.warning(f"Configuration file not found at {self.config_path}. Proceeding with default or environment variable configurations.")
            self.config = {}

        # Override with environment variables
        self._override_with_env_vars(self.config)

    def _override_with_env_vars(self, config_dict: Dict[str, Any], prefix: str = ""):
        """
        Recursively override configuration with environment variables.
        Example: config {'gcp': {'project_id': 'x'}} looks for env var GCP_PROJECT_ID.
        """
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self._override_with_env_vars(value, prefix=f"{prefix}{key}_")
            else:
                env_var_name = (prefix + key).upper()
                env_value = os.getenv(env_var_name)
                if env_value is not None:
                    try:
                        original_type = type(value) if value is not None else str
                        if original_type == bool:
                            config_dict[key] = env_value.lower() in ('true', '1', 't', 'yes')
                        elif original_type == int:
                            config_dict[key] = int(env_value)
                        elif original_type == float:
                            config_dict[key] = float(env_value)
                        else:
                            config_dict[key] = env_value
                        logger.info(f"Overriding config '{prefix}{key}' with value from environment variable '{env_var_name}'.")
                    except (ValueError, TypeError):
                        config_dict[key] = env_value
                        logger.warning(f"Could not cast env var '{env_var_name}' to type {original_type}. Using string value '{env_value}'.")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation for nested keys.

        Args:
            key: The configuration key to retrieve (e.g., 'gcp.project_id').
            default: The default value to return if the key is not found.

        Returns:
            The configuration value.
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary-style access.
        Does not support dot notation. Raises KeyError if the key is not found.
        """
        return self.config[key]

    def __repr__(self) -> str:
        """
        Return a string representation of the ConfigManager instance.
        """
        return f"ConfigManager(config_path='{self.config_path}')"
