from __future__ import annotations

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.models.analyzers import ALL_ANALYZERS
from src.views.chart_widget import ChartWidget
from src.views.conclusions_panel import ConclusionsPanel
from src.views.data_table_view import DataTableView
from src.views.filters_panel import FiltersPanel


class MainWindow(QMainWindow):
    """Main window: menu, splitter, tabs, status bar.

    Signals:
        analysis_selected: Emitted with the class name of the analyzer
            selected in the "Analiza" menu.
        refresh_requested: Emitted on refresh (F5).
    """

    analysis_selected = pyqtSignal(str)
    refresh_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Stack Overflow Survey - analiza (PyQt6 / MVC)")
        self.resize(1100, 720)

        self.filters_panel = FiltersPanel()
        self.table_view = DataTableView()
        self.chart_widget = ChartWidget()
        self.conclusions_panel = ConclusionsPanel()

        self._build_central_widget()
        self._build_menu()
        self._build_shortcuts()
        self.statusBar().showMessage("Gotowy.")

    def _build_central_widget(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.addTab(self.table_view, "Tabela")
        self.tabs.addTab(self.chart_widget, "Wykres")

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(self.tabs, stretch=3)
        right_layout.addWidget(self.conclusions_panel, stretch=1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.filters_panel)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 880])

        self.setCentralWidget(splitter)

    def _build_menu(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("&Plik")
        quit_action = QAction("Zamknij", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        analysis_menu = menu.addMenu("&Analiza")
        for analyzer_cls in ALL_ANALYZERS:
            action = QAction(analyzer_cls.name, self)
            action.triggered.connect(
                lambda _checked=False, n=analyzer_cls.__name__: self.analysis_selected.emit(n)
            )
            analysis_menu.addAction(action)

        help_menu = menu.addMenu("&Pomoc")
        about = QAction("O programie", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _build_shortcuts(self) -> None:
        refresh = QAction(self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(self.refresh_requested.emit)
        self.addAction(refresh)

    def _show_about(self) -> None:
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "O programie",
            "Analiza Stack Overflow Developer Survey 2024.\n"
            "Architektura MVC, PyQt6 + pandas + matplotlib/seaborn.",
        )

    def set_status(self, message: str) -> None:
        """Set the message on the status bar."""
        self.statusBar().showMessage(message)
