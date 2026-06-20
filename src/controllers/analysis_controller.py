from __future__ import annotations
import pandas as pd

from src.models.analyzers import ALL_ANALYZERS, Analyzer, PopularityAnalyzer
from src.models.data_pipeline import DataPipeline
from src.utils import constants as const
from src.views.main_window import MainWindow


class AnalysisController:
    """Application controller in the MVC architecture."""

    def __init__(self, window: MainWindow, pipeline: DataPipeline) -> None:
        self.window = window
        self.pipeline = pipeline
        self.current_analyzer: Analyzer = PopularityAnalyzer()
        self._analyzers = {cls.__name__: cls for cls in ALL_ANALYZERS}
        self._current_filters: dict = {}

        self._connect_signals()
        self._initialize_views()

    def _connect_signals(self) -> None:
        self.window.filters_panel.filters_changed.connect(self._on_filters_changed)
        self.window.analysis_selected.connect(self._on_analysis_selected)
        self.window.refresh_requested.connect(self._refresh)
        self.window.chart_widget.render_error.connect(
            lambda msg: self.window.set_status(f"Błąd wykresu: {msg}")
        )

    def _initialize_views(self) -> None:
        df = self.pipeline.df
        self.window.filters_panel.populate(df)
        self.window.table_view.set_dataframe(df)
        self._run_analysis(df)
        self.window.set_status(f"Wczytano {len(df):,} rekordów.")

    def _on_filters_changed(self, filters: dict) -> None:
        self._current_filters = filters
        self._refresh()

    def _on_analysis_selected(self, name: str) -> None:
        analyzer_cls = self._analyzers.get(name)
        if analyzer_cls is None:
            return
        self.current_analyzer = analyzer_cls()
        self.window.tabs.setCurrentIndex(1)
        self._refresh()

    def _refresh(self) -> None:
        df = self._apply_filters(self.pipeline.df, self._current_filters)
        self.window.table_view.set_dataframe(df)
        self._run_analysis(df)
        self.window.set_status(self._status_text(df))

    def _run_analysis(self, df: pd.DataFrame) -> None:
        analyzer = self.current_analyzer
        try:
            result = analyzer.run(df)
        except KeyError as exc:
            self.window.set_status(f"Brak wymaganej kolumny: {exc}")
            self.window.conclusions_panel.set_text(
                "Wybrana analiza wymaga kolumny niedostępnej w danych."
            )
            return

        self.window.chart_widget.plot(result, analyzer.chart_type(), analyzer.name)
        self.window.conclusions_panel.set_text(analyzer.describe(result))

    def _apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        if not filters:
            return df
        mask = pd.Series(True, index=df.index)

        country = filters.get("country", const.FILTER_ALL)
        if country and country != const.FILTER_ALL and const.COL_COUNTRY in df.columns:
            mask &= df[const.COL_COUNTRY] == country

        language = filters.get("language", const.FILTER_ALL)
        if language and language != const.FILTER_ALL and "LanguageList" in df.columns:
            mask &= df["LanguageList"].apply(
                lambda langs: isinstance(langs, list) and language in langs
            )

        if const.COL_YEARS_PRO in df.columns:
            years = df[const.COL_YEARS_PRO]
            min_exp = filters.get("min_exp", 0)
            max_exp = filters.get("max_exp", 50)
            mask &= years.isna() | years.between(min_exp, max_exp)

        return df[mask]

    def _status_text(self, df: pd.DataFrame) -> str:
        parts = [f"Rekordów: {len(df):,}"]
        country = self._current_filters.get("country", const.FILTER_ALL)
        if country and country != const.FILTER_ALL:
            parts.append(f"Kraj: {country}")
        language = self._current_filters.get("language", const.FILTER_ALL)
        if language and language != const.FILTER_ALL:
            parts.append(f"Język: {language}")
        return " | ".join(parts)
