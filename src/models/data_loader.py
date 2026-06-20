from __future__ import annotations

import os

import pandas as pd


class DataLoader:
    """Singleton that loads and stores the raw dataset."""

    _instance: "DataLoader | None" = None
    _df: pd.DataFrame | None = None

    def __new__(cls, path: str = "") -> "DataLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, path: str) -> pd.DataFrame:
        """Load the CSV file (once - later calls return the cache).

        Args:
            path: Path to the CSV file.

        Returns:
            The loaded DataFrame with raw data.

        Raises:
            FileNotFoundError: When the file does not exist.
            pd.errors.ParserError: When the file cannot be parsed.
        """
        if self._df is not None:
            return self._df

        if not os.path.exists(path):
            raise FileNotFoundError(f"Nie znaleziono pliku danych: {path}")

        try:
            self._df = pd.read_csv(path, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            self._df = pd.read_csv(path, low_memory=False, encoding="latin-1")

        return self._df

    @property
    def df(self) -> pd.DataFrame | None:
        """The currently loaded DataFrame (or None)."""
        return self._df

    @classmethod
    def reset(cls) -> None:
        """Clear the cache - useful in unit tests."""
        cls._instance = None
        cls._df = None
