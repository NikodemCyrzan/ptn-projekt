"""Unit tests for data loading (Singleton)."""

import pandas as pd
import pytest

from src.models.data_loader import DataLoader

@pytest.fixture(autouse=True)
def _reset_loader():
    """Reset the singleton before and after each test."""
    DataLoader.reset()
    yield
    DataLoader.reset()


def test_missing_file():
    """Missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        DataLoader().load("nonexistent.csv")


def test_singleton_identity():
    """Every constructor call returns the same object."""
    assert DataLoader() is DataLoader()


def test_load_and_cache(tmp_path):
    """Data is loaded once and returned from the cache."""
    csv = tmp_path / "data.csv"
    csv.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    loader = DataLoader()
    df1 = loader.load(str(csv))
    assert isinstance(df1, pd.DataFrame)
    assert df1.shape == (2, 2)

    df2 = loader.load(str(csv))
    assert df1 is df2
