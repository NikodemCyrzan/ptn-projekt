from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from src.utils import constants as const


class Analyzer(ABC):
    """Base analysis interface (Strategy interface)."""

    name: str = "Analiza"

    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run the analysis and return the result as a DataFrame."""

    @abstractmethod
    def describe(self, result: pd.DataFrame) -> str:
        """Generate textual conclusions based on the result."""

    @abstractmethod
    def chart_type(self) -> str:
        """Return the chart type: 'barh', 'boxplot', 'bar', 'heatmap'."""

    def _empty_msg(self) -> str:
        return "Brak danych spełniających kryteria filtrowania."


class SalaryAnalyzer(Analyzer):
    """Median/quartiles of salaries grouped by country."""

    name = "Wynagrodzenia wg krajów"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or const.COL_SALARY not in df.columns:
            return pd.DataFrame(columns=["median", "mean", "count"])
        return (
            df.dropna(subset=[const.COL_SALARY])
            .groupby(const.COL_COUNTRY)[const.COL_SALARY]
            .agg(["median", "mean", "count"])
            .query(f"count >= {const.MIN_GROUP_SIZE}")
            .sort_values("median", ascending=False)
            .head(20)
        )

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        top = result.index[0]
        val = result.loc[top, "median"]
        bottom = result.index[-1]
        bottom_val = result.loc[bottom, "median"]
        return (
            f"Najwyższa mediana wynagrodzeń: {top} ({val:,.0f} USD).\n"
            f"Najniższa w tym zestawieniu: {bottom} ({bottom_val:,.0f} USD).\n"
            f"Dysproporcja między skrajnymi krajami: "
            f"{val / bottom_val:.1f}x (przy min. {const.MIN_GROUP_SIZE} "
            f"respondentach na kraj)."
        )

    def chart_type(self) -> str:
        return "barh"


class PopularityAnalyzer(Analyzer):
    """Ranking of the most popular programming languages."""

    name = "Popularność języków"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or const.COL_LANGUAGES not in df.columns:
            return pd.DataFrame(columns=["count"])
        counts = (
            df[const.COL_LANGUAGES]
            .dropna()
            .str.split(";")
            .explode()
            .str.strip()
            .value_counts()
            .head(20)
        )
        return counts.rename("count").to_frame()

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        top3 = ", ".join(result.index[:3])
        leader = result.index[0]
        leader_val = int(result.loc[leader, "count"])
        return (
            f"Najpopularniejsze języki: {top3}.\n"
            f"Lider zestawienia ({leader}) pojawia się w {leader_val:,} "
            f"odpowiedziach."
        )

    def chart_type(self) -> str:
        return "barh"


class ExperienceSalaryAnalyzer(Analyzer):
    """Salary distribution across ranges of professional experience."""

    name = "Wynagrodzenie vs doświadczenie"

    _BINS = [0, 2, 5, 10, 20, 100]
    _LABELS = ["0-2", "3-5", "6-10", "11-20", "20+"]

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = {const.COL_YEARS_PRO, const.COL_SALARY}
        if df.empty or not cols.issubset(df.columns):
            return pd.DataFrame(columns=[const.COL_SALARY, "ExpBucket"])
        data = df.dropna(subset=[const.COL_YEARS_PRO, const.COL_SALARY]).copy()
        data = data[data[const.COL_SALARY] <= 1_000_000]
        data["ExpBucket"] = pd.cut(
            data[const.COL_YEARS_PRO],
            bins=self._BINS,
            labels=self._LABELS,
            right=True,
            include_lowest=True,
        )
        return data[[const.COL_SALARY, "ExpBucket"]].dropna(subset=["ExpBucket"])

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        medians = result.groupby("ExpBucket", observed=True)[const.COL_SALARY].median()
        if medians.empty:
            return self._empty_msg()
        junior = medians.iloc[0]
        senior = medians.iloc[-1]
        ratio = senior / junior if junior else float("nan")
        return (
            f"Mediana wynagrodzeń rośnie z doświadczeniem: od "
            f"{junior:,.0f} USD ({medians.index[0]} lat) do "
            f"{senior:,.0f} USD ({medians.index[-1]} lat) - wzrost "
            f"ok. {ratio:.1f}x."
        )

    def chart_type(self) -> str:
        return "boxplot"


class SatisfactionAnalyzer(Analyzer):
    """Job satisfaction by work mode (remote/hybrid/in-office)."""

    name = "Satysfakcja vs tryb pracy"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = {const.COL_REMOTE, const.COL_JOB_SAT}
        if df.empty or not cols.issubset(df.columns):
            return pd.DataFrame(columns=["mean", "median", "count"])
        return (
            df.dropna(subset=[const.COL_REMOTE, const.COL_JOB_SAT])
            .groupby(const.COL_REMOTE)[const.COL_JOB_SAT]
            .agg(["mean", "median", "count"])
            .sort_values("mean", ascending=False)
        )

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        best = result.index[0]
        best_val = result.loc[best, "mean"]
        worst = result.index[-1]
        worst_val = result.loc[worst, "mean"]
        return (
            f"Najwyższa średnia satysfakcja: '{best}' ({best_val:.2f}/10).\n"
            f"Najniższa: '{worst}' ({worst_val:.2f}/10).\n"
            f"Różnica między trybami pracy wynosi {best_val - worst_val:.2f} pkt."
        )

    def chart_type(self) -> str:
        return "bar"


class AISalaryAnalyzer(Analyzer):
    """Comparison of salaries and satisfaction by AI tool usage."""

    name = "AI vs wynagrodzenie/satysfakcja"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = {const.COL_AI_SELECT, const.COL_SALARY}
        if df.empty or not cols.issubset(df.columns):
            return pd.DataFrame(columns=["salary_median", "jobsat_mean", "count"])
        data = df.dropna(subset=[const.COL_AI_SELECT])
        agg = {const.COL_SALARY: "median"}
        if const.COL_JOB_SAT in data.columns:
            agg[const.COL_JOB_SAT] = "mean"
        result = data.groupby(const.COL_AI_SELECT).agg(agg)
        result["count"] = data.groupby(const.COL_AI_SELECT).size()
        rename = {const.COL_SALARY: "salary_median", const.COL_JOB_SAT: "jobsat_mean"}
        return result.rename(columns=rename).sort_values("salary_median", ascending=False)

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        top = result.index[0]
        top_val = result.loc[top, "salary_median"]
        return (
            f"Najwyższa mediana wynagrodzeń wśród grup AI: '{top}' "
            f"({top_val:,.0f} USD).\n"
            "Wykres porównuje medianę zarobków w grupach wg deklarowanego "
            "użycia narzędzi AI."
        )

    def chart_type(self) -> str:
        return "bar"


class CorrelationAnalyzer(Analyzer):
    """Correlation matrix of numeric variables."""

    name = "Korelacje zmiennych numerycznych"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        cols = [c for c in const.NUMERIC_COLUMNS if c in df.columns]
        numeric = df[cols].apply(pd.to_numeric, errors="coerce")
        numeric = numeric.dropna(how="all", axis=1)
        if numeric.shape[1] < 2:
            return pd.DataFrame()
        return numeric.corr()

    def describe(self, result: pd.DataFrame) -> str:
        if result.empty:
            return self._empty_msg()
        corr = result.copy()
        for col in corr.columns:
            corr.loc[col, col] = 0.0
        stacked = corr.abs().stack()
        if stacked.empty:
            return "Brak wystarczających danych numerycznych do korelacji."
        a, b = stacked.idxmax()
        value = result.loc[a, b]
        return (
            f"Najsilniejsza zależność liniowa: {a} <-> {b} "
            f"(r = {value:.2f}).\n"
            "Wartości bliskie 1/-1 oznaczają silną korelację, bliskie 0 - brak."
        )

    def chart_type(self) -> str:
        return "heatmap"


ALL_ANALYZERS: list[type[Analyzer]] = [
    PopularityAnalyzer,
    SalaryAnalyzer,
    ExperienceSalaryAnalyzer,
    SatisfactionAnalyzer,
    AISalaryAnalyzer,
    CorrelationAnalyzer,
]
