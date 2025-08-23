import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

class ConfigManager:
    """A class to manage configuration for the FinOps analysis platform."""

    def __init__(self, config_path: str = 'config.yaml', env_path: str = '.env'):
        """
        Initialize the ConfigManager.

        Args:
            config_path: The path to the YAML configuration file.
            env_path: The path to the .env file.
        """
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self.config = {}
        self.load_config()

    def load_config(self):
        """
        Load the configuration from the YAML file and override with environment variables.
        """
        # Load environment variables from .env file
        load_dotenv(dotenv_path=self.env_path)

        # Load base configuration from YAML file
        if self.config_path.is_file():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            print(f"Warning: Configuration file not found at {self.config_path}")
            self.config = {}

        # Override with environment variables
        for key, value in os.environ.items():
            # For nested keys, we can use a simple dot notation for environment variables
            # e.g., GCP_PROJECT_ID will override gcp.project_id
            keys = key.lower().split('_')
            if len(keys) > 1:
                section = keys[0]
                section_key = '_'.join(keys[1:])
                if section in self.config and section_key in self.config[section]:
                    self.config[section][section_key] = value

    def get(self, key, default=None):
        """
        Get a configuration value.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value.
        """
        return self.config.get(key, default)

    def __getitem__(self, key):
        """
        Get a configuration value using dictionary-style access.
        """
        return self.config[key]

if __name__ == '__main__':
    # Example usage
    config_manager = ConfigManager()
    print("Loaded configuration:")
    print(config_manager.config)

    # Example of accessing a value
    gcp_project = config_manager.get('gcp', {}).get('project_id')
    print(f"\nGCP Project ID: {gcp_project}")
