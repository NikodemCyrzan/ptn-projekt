from __future__ import annotations

import pandas as pd

from src.models.data_cleaner import DataCleaner
from src.models.data_loader import DataLoader


class DataPipeline:
    """Facade: load then clean in a single call.

    Args:
        path: Path to the CSV file with survey data.

    Attributes:
        raw: Raw DataFrame after loading.
        df: Cleaned DataFrame ready for analysis.
    """

    def __init__(self, path: str) -> None:
        self.raw: pd.DataFrame = DataLoader().load(path)
        self.df: pd.DataFrame = DataCleaner(self.raw).clean()

    def __len__(self) -> int:
        return len(self.df)
