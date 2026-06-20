from __future__ import annotations

import matplotlib

matplotlib.use("QtAgg")

import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.utils import constants as const


class ChartWidget(QWidget):
    """A Matplotlib canvas wrapped in a Qt widget.

    Signals:
        render_error: Emitted with an error message when drawing fails.
    """

    render_error = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self._show_placeholder("Wybierz analizę z menu 'Analiza'.")

    def plot(self, result: pd.DataFrame, chart_type: str, title: str = "") -> None:
        """Draw the analysis result with the appropriate chart type.

        Args:
            result: The DataFrame returned by the analyzer.
            chart_type: One of: barh, bar, boxplot, heatmap.
            title: The chart title.
        """
        try:
            self.figure.clear()
            if result is None or result.empty:
                self._show_placeholder("Brak danych do wyświetlenia.")
                return

            ax = self.figure.add_subplot(111)
            dispatch = {
                "barh": self._plot_barh,
                "bar": self._plot_bar,
                "boxplot": self._plot_boxplot,
                "heatmap": self._plot_heatmap,
            }
            painter = dispatch.get(chart_type, self._plot_bar)
            painter(ax, result)

            if title:
                ax.set_title(title)
            self.canvas.draw()
        except Exception as exc:
            self._show_placeholder("Błąd renderowania wykresu.")
            self.render_error.emit(str(exc))

    def _plot_barh(self, ax, result: pd.DataFrame) -> None:
        col = "median" if "median" in result.columns else result.columns[0]
        data = result[col].iloc[::-1]
        colors = sns.color_palette(const.PALETTE, len(data))
        ax.barh(data.index.astype(str), data.values, color=colors)
        ax.set_xlabel(col)

    def _plot_bar(self, ax, result: pd.DataFrame) -> None:
        col = "mean" if "mean" in result.columns else result.columns[0]
        data = result[col]
        colors = sns.color_palette(const.PALETTE, len(data))
        ax.bar(data.index.astype(str), data.values, color=colors)
        ax.set_ylabel(col)
        ax.tick_params(axis="x", rotation=20)

    def _plot_boxplot(self, ax, result: pd.DataFrame) -> None:
        sns.boxplot(
            data=result,
            x="ExpBucket",
            y=const.COL_SALARY,
            hue="ExpBucket",
            legend=False,
            ax=ax,
            palette=const.PALETTE,
            showfliers=False,
        )
        ax.set_xlabel("Lata doświadczenia zawodowego")
        ax.set_ylabel("Wynagrodzenie roczne (USD)")

    def _plot_heatmap(self, ax, result: pd.DataFrame) -> None:
        sns.heatmap(
            result,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            vmin=-1,
            vmax=1,
            ax=ax,
        )

    def _show_placeholder(self, text: str) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=11, color="gray")
        ax.axis("off")
        self.canvas.draw()
