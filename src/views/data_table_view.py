from __future__ import annotations

import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import (
    QHeaderView,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class PandasModel(QAbstractTableModel):
    """Adapter from DataFrame to QAbstractTableModel."""

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()
        self._df = df

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._df)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else self._df.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        value = self._df.iat[index.row(), index.column()]
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        return "" if pd.isna(value) else str(value)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._df.columns[section])
        return str(self._df.index[section])

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Replace the presented data."""
        self.beginResetModel()
        self._df = df
        self.endResetModel()


class DataTableView(QWidget):
    """Table view: a search box plus a sortable QTableView."""

    MAX_ROWS = 2000

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._source = PandasModel(pd.DataFrame())
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._source)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Szukaj w tabeli...")
        self.search.textChanged.connect(self._proxy.setFilterFixedString)

        self.table = QTableView()
        self.table.setModel(self._proxy)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.table)

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Load a DataFrame into the table (truncated to MAX_ROWS)."""
        self._source.set_dataframe(df.head(self.MAX_ROWS).reset_index(drop=True))
