"""Manages mapping of GCP machine types to their respective discount rates."""

import logging
from pathlib import Path
from typing import Dict, Optional, cast

import yaml

logger = logging.getLogger(__name__)


class MachineTypeDiscountMapping:
    """
    Manages mapping of GCP machine types to their respective discount rates.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initializes the discount mapping from a YAML configuration file."""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "machine_discounts.yaml"
        config = self._load_discounts(str(config_path))
        self.discounts = cast(Dict[str, Dict[str, float]], config.get("discounts", {}))
        self.prefixes: list[str] = list(self.discounts.keys())
        self.families = cast(Dict[str, list[str]], config.get("families", {}))

    def _load_discounts(self, file_path: str) -> Dict:
        """Loads the machine discounts from a YAML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                return yaml.safe_load(file_handle) or {}
        except (FileNotFoundError, yaml.YAMLError) as exception:
            logger.error("Failed to load discount mapping file: %s", exception)
            return {}

    def get_discount(self, machine_type: str, discount_type: str) -> Optional[float]:
        """Gets the discount for a given machine type and discount type."""
        machine_base = self._extract_machine_base(machine_type)
        return self.discounts.get(machine_base, {}).get(discount_type)

    def _extract_machine_base(self, machine_type: str) -> str:
        """Extracts the base machine type from a full SKU description."""
        machine_type = machine_type.lower()
        for prefix in self.prefixes:
            if machine_type.startswith(prefix):
                return prefix

        # Fallback for machine types not explicitly in prefixes (like 'n1')
        parts = machine_type.split("-")
        if parts:
            return parts[0]

        logger.debug(
            "Could not determine base type for '%s', defaulting to 'n2'.", machine_type
        )
        return "n2"

    def get_machine_base(self, machine_type: str) -> str:
        """Public method to get machine base type."""
        return self._extract_machine_base(machine_type)

    def get_family(self, machine_type: str) -> str:
        """Gets the machine family for a given machine type."""
        machine_base = self._extract_machine_base(machine_type)
        for family, types in self.families.items():
            if machine_base in types:
                return family
        return "General Purpose"
