from __future__ import annotations

import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.utils import constants as const


class FiltersPanel(QWidget):
    """Side panel with filters: country, language, experience year range.

    Signals:
        filters_changed: Emitted with a dict of filters after clicking
            "Filtruj" or changing a value.
    """

    filters_changed = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaximumWidth(240)

        self.country_combo = QComboBox()
        self.language_combo = QComboBox()

        self.min_exp = QSlider(Qt.Orientation.Horizontal)
        self.min_exp.setRange(0, 50)
        self.max_exp = QSlider(Qt.Orientation.Horizontal)
        self.max_exp.setRange(0, 50)
        self.max_exp.setValue(50)
        self.exp_label = QLabel()

        self.min_exp.valueChanged.connect(self._update_exp_label)
        self.max_exp.valueChanged.connect(self._update_exp_label)
        self._update_exp_label()

        self.apply_btn = QPushButton("Filtruj")
        self.reset_btn = QPushButton("Reset")
        self.apply_btn.clicked.connect(self._emit_filters)
        self.reset_btn.clicked.connect(self.reset)

        self._build_layout()

    def _build_layout(self) -> None:
        box = QGroupBox("Filtry")
        inner = QVBoxLayout(box)
        inner.addWidget(QLabel("Kraj:"))
        inner.addWidget(self.country_combo)
        inner.addWidget(QLabel("Język:"))
        inner.addWidget(self.language_combo)
        inner.addWidget(QLabel("Doświadczenie (lata):"))
        inner.addWidget(self.min_exp)
        inner.addWidget(self.max_exp)
        inner.addWidget(self.exp_label)
        inner.addStretch(1)
        inner.addWidget(self.apply_btn)
        inner.addWidget(self.reset_btn)

        outer = QVBoxLayout(self)
        outer.addWidget(box)

    def populate(self, df: pd.DataFrame) -> None:
        """Fill the drop-down lists with values from the data.

        Args:
            df: The cleaned source DataFrame.
        """
        self.country_combo.clear()
        self.language_combo.clear()
        self.country_combo.addItem(const.FILTER_ALL)
        self.language_combo.addItem(const.FILTER_ALL)

        if const.COL_COUNTRY in df.columns:
            countries = sorted(df[const.COL_COUNTRY].dropna().unique())
            self.country_combo.addItems([str(c) for c in countries])

        if "LanguageList" in df.columns:
            langs = (
                df["LanguageList"].dropna().explode().dropna().unique()
            )
            self.language_combo.addItems(sorted({str(x) for x in langs}))

    def _update_exp_label(self) -> None:
        if self.min_exp.value() > self.max_exp.value():
            self.max_exp.setValue(self.min_exp.value())
        self.exp_label.setText(
            f"{self.min_exp.value()}-{self.max_exp.value()} lat"
        )

    def _collect_filters(self) -> dict:
        return {
            "country": self.country_combo.currentText(),
            "language": self.language_combo.currentText(),
            "min_exp": self.min_exp.value(),
            "max_exp": self.max_exp.value(),
        }

    def _emit_filters(self) -> None:
        self.filters_changed.emit(self._collect_filters())

    def reset(self) -> None:
        """Reset the filters to their default state and emit the signal."""
        self.country_combo.setCurrentIndex(0)
        self.language_combo.setCurrentIndex(0)
        self.min_exp.setValue(0)
        self.max_exp.setValue(50)
        self._emit_filters()
