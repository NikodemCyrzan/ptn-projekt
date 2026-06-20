import pandas as pd

from src.models.analyzers import (
    CorrelationAnalyzer,
    ExperienceSalaryAnalyzer,
    PopularityAnalyzer,
    SalaryAnalyzer,
    SatisfactionAnalyzer,
)


def test_salary_analyzer_top_country():
    """The result has median, mean, count columns and is sorted descending."""
    df = pd.DataFrame(
        {
            "Country": ["PL"] * 50 + ["US"] * 50,
            "ConvertedCompYearly": [40000.0] * 50 + [100000.0] * 50,
        }
    )
    result = SalaryAnalyzer().run(df)
    assert list(result.columns) == ["median", "mean", "count"]
    assert result.index[0] == "US"
    assert result.loc["US", "median"] == 100000


def test_salary_analyzer_filters_small_groups():
    """Countries with fewer than 30 respondents are skipped."""
    df = pd.DataFrame(
        {
            "Country": ["PL"] * 50 + ["XX"] * 5,
            "ConvertedCompYearly": [40000.0] * 50 + [999999.0] * 5,
        }
    )
    result = SalaryAnalyzer().run(df)
    assert "XX" not in result.index
    assert "PL" in result.index


def test_analyzer_empty_df():
    """An empty DataFrame does not raise - it returns an empty result."""
    assert len(SalaryAnalyzer().run(pd.DataFrame())) == 0
    assert len(PopularityAnalyzer().run(pd.DataFrame())) == 0
    assert len(SatisfactionAnalyzer().run(pd.DataFrame())) == 0
    assert len(ExperienceSalaryAnalyzer().run(pd.DataFrame())) == 0
    assert len(CorrelationAnalyzer().run(pd.DataFrame())) == 0


def test_popularity_analyzer_counts_languages():
    """Splits multiple-choice fields and counts language occurrences."""
    df = pd.DataFrame(
        {
            "LanguageHaveWorkedWith": [
                "Python;JavaScript",
                "Python;Go",
                "Python",
            ]
        }
    )
    result = PopularityAnalyzer().run(df)
    assert result.loc["Python", "count"] == 3
    assert result.loc["Go", "count"] == 1
    assert result.index[0] == "Python"


def test_satisfaction_analyzer_groups_by_remote():
    """Groups satisfaction by work mode and computes the mean."""
    df = pd.DataFrame(
        {
            "RemoteWork": ["Remote", "Remote", "In-person", "In-person"],
            "JobSat": [10.0, 8.0, 4.0, 2.0],
        }
    )
    result = SatisfactionAnalyzer().run(df)
    assert result.loc["Remote", "mean"] == 9.0
    assert result.loc["In-person", "mean"] == 3.0
    assert result.index[0] == "Remote"


def test_experience_salary_buckets():
    """Creates experience buckets and clips extreme salaries."""
    df = pd.DataFrame(
        {
            "YearsCodePro": [1, 4, 8, 25],
            "ConvertedCompYearly": [30000.0, 60000.0, 90000.0, 5_000_000.0],
        }
    )
    result = ExperienceSalaryAnalyzer().run(df)
    assert "ExpBucket" in result.columns
    assert result["ConvertedCompYearly"].max() <= 1_000_000


def test_describe_returns_string():
    """describe() always returns a string, also for an empty result."""
    analyzer = SalaryAnalyzer()
    empty = analyzer.run(pd.DataFrame())
    assert isinstance(analyzer.describe(empty), str)


def test_correlation_matrix_is_square():
    """The correlation matrix is square for numeric data."""
    df = pd.DataFrame(
        {
            "ConvertedCompYearly": [1.0, 2.0, 3.0, 4.0],
            "YearsCodePro": [1.0, 2.0, 3.0, 4.0],
            "JobSat": [4.0, 3.0, 2.0, 1.0],
        }
    )
    result = CorrelationAnalyzer().run(df)
    assert result.shape[0] == result.shape[1]
    assert result.shape[0] >= 2
