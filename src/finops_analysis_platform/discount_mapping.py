"""Manages mapping of GCP machine types to their respective discount rates."""

import logging
from pathlib import Path
from typing import Optional

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
        self._load_discounts_from_yaml(config_path)

    def _load_discounts_from_yaml(self, path: Path):
        """Loads discount data from the specified YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.discounts = data.get("discounts", {})
                self.families = data.get("families", {})
                self.prefixes = data.get("prefixes", [])
                logger.info(
                    "Loaded %d machine types from %s", len(self.discounts), path
                )
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.error("Error with discount config file %s: %s", path, e)
            self.discounts, self.families, self.prefixes = {}, {}, []

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
