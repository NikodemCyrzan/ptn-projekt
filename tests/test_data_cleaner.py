"""Unit tests for data cleaning."""

import pandas as pd

from src.models.data_cleaner import DataCleaner


def test_parse_multi_choice():
    """Column 'Python;JavaScript' becomes list ['Python', 'JavaScript']."""
    row = pd.DataFrame({"LanguageHaveWorkedWith": ["Python;JavaScript"]})
    result = DataCleaner(row).parse_multi_choice("LanguageHaveWorkedWith")
    assert result.iloc[0] == ["Python", "JavaScript"]


def test_parse_multi_choice_strips_whitespace():
    """Whitespace around items is stripped."""
    row = pd.DataFrame({"L": ["C# ; Rust ;Go"]})
    result = DataCleaner(row).parse_multi_choice("L")
    assert result.iloc[0] == ["C#", "Rust", "Go"]


def test_parse_multi_choice_nan_stays_nan():
    """A missing value stays missing (NaN), not an empty list."""
    row = pd.DataFrame({"L": [None]})
    result = DataCleaner(row).parse_multi_choice("L")
    assert pd.isna(result.iloc[0])


def test_salary_conversion():
    """String '85000' becomes float 85000.0, and 'NA' becomes NaN."""
    row = pd.DataFrame({"ConvertedCompYearly": ["85000", "NA"]})
    result = DataCleaner(row).convert_salary()
    assert result["ConvertedCompYearly"].iloc[0] == 85000.0
    assert pd.isna(result["ConvertedCompYearly"].iloc[1])


def test_convert_years_special_values():
    """'Less than 1 year' becomes 0, 'More than 50 years' becomes 51."""
    row = pd.DataFrame(
        {
            "YearsCode": ["Less than 1 year", "More than 50 years", "10"],
            "YearsCodePro": ["5", "Less than 1 year", "NA"],
        }
    )
    result = DataCleaner(row).convert_years()
    assert result["YearsCode"].iloc[0] == 0
    assert result["YearsCode"].iloc[1] == 51
    assert result["YearsCode"].iloc[2] == 10
    assert pd.isna(result["YearsCodePro"].iloc[2])


def test_clean_creates_language_list():
    """The full pipeline creates a LanguageList column with language lists."""
    raw = pd.DataFrame(
        {
            "LanguageHaveWorkedWith": ["Python;Go", None],
            "ConvertedCompYearly": ["1000", "NA"],
            "YearsCode": ["3", "Less than 1 year"],
            "YearsCodePro": ["1", "2"],
            "JobSat": ["8", "5"],
        }
    )
    cleaned = DataCleaner(raw).clean()
    assert cleaned["LanguageList"].iloc[0] == ["Python", "Go"]
    assert cleaned["ConvertedCompYearly"].iloc[0] == 1000.0


def test_cleaner_does_not_mutate_input():
    """DataCleaner works on a copy - the original stays untouched."""
    raw = pd.DataFrame({"ConvertedCompYearly": ["100"]})
    DataCleaner(raw).convert_salary()
    assert raw["ConvertedCompYearly"].iloc[0] == "100"
