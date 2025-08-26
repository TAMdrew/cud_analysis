"""Defines the protocol for data loaders."""

from typing import Dict, Protocol, Union

import pandas as pd


class DataLoader(Protocol):
    """Protocol for data loaders."""

    def load_all_data(self) -> Dict[str, Union[pd.DataFrame, bool]]:
        """Loads all data from the data source."""
        ...
