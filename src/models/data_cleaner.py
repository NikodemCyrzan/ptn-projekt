from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import constants as const


class DataCleaner:
    """Clean and convert the raw survey DataFrame.

    Operates on a copy of the given data, so the original stays untouched.

    Args:
        df: Raw DataFrame loaded by DataLoader.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def convert_salary(self) -> pd.DataFrame:
        """Convert the salary column to a floating-point type.

        Non-numeric values (e.g. "NA") become NaN.

        Returns:
            DataFrame with the salary column as float.
        """
        if const.COL_SALARY in self.df.columns:
            self.df[const.COL_SALARY] = pd.to_numeric(
                self.df[const.COL_SALARY], errors="coerce"
            )
        return self.df

    def convert_years(self) -> pd.DataFrame:
        """Convert the years-of-experience columns to numbers.

        Maps the survey text values: "Less than 1 year" to 0,
        "More than 50 years" to 51.

        Returns:
            DataFrame with the converted year columns.
        """
        mapping = {"Less than 1 year": 0, "More than 50 years": 51}
        for col in (const.COL_YEARS_CODE, const.COL_YEARS_PRO):
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(
                    self.df[col].replace(mapping), errors="coerce"
                )
        return self.df

    def parse_multi_choice(self, column: str) -> pd.Series:
        """Split a multiple-choice field into a list of answers.

        Args:
            column: Name of the column with values separated by ";".

        Returns:
            A Series where each cell is a list of strings (or NaN).

        Examples:
            >>> import pandas as pd
            >>> df = pd.DataFrame({"L": ["Python;JavaScript"]})
            >>> DataCleaner(df).parse_multi_choice("L").iloc[0]
            ['Python', 'JavaScript']
        """
        def _split(value: object) -> object:
            if pd.isna(value):
                return np.nan
            return [item.strip() for item in str(value).split(";") if item.strip()]

        return self.df[column].apply(_split)

    def convert_job_sat(self) -> pd.DataFrame:
        """Convert the job-satisfaction column to numbers from 0 to 10."""
        if const.COL_JOB_SAT in self.df.columns:
            self.df[const.COL_JOB_SAT] = pd.to_numeric(
                self.df[const.COL_JOB_SAT], errors="coerce"
            )
        return self.df

    def clean(self) -> pd.DataFrame:
        """Run the full data-cleaning pipeline.

        Combines the numeric conversions and multiple-choice parsing in one
        call. Creates a helper LanguageList column with lists of languages,
        used by the analyzers and filters.

        Returns:
            A cleaned DataFrame ready for analysis.
        """
        self.convert_salary()
        self.convert_years()
        self.convert_job_sat()

        if const.COL_LANGUAGES in self.df.columns:
            self.df["LanguageList"] = self.parse_multi_choice(const.COL_LANGUAGES)

        return self.df
