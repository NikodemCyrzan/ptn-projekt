from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from src.models.data_pipeline import DataPipeline
from src.utils import constants as const


def _load_pipeline(app: QApplication, path: str) -> DataPipeline | None:
    while True:
        try:
            return DataPipeline(path)
        except FileNotFoundError:
            QMessageBox.critical(
                None, "Błąd", f"Nie znaleziono pliku:\n{path}"
            )
        except Exception as exc:
            QMessageBox.critical(
                None, "Błąd wczytywania", f"Nie udało się wczytać danych:\n{exc}"
            )

        chosen, _ = QFileDialog.getOpenFileName(
            None, "Wskaż plik CSV z danymi ankiety", "", "CSV (*.csv)"
        )
        if not chosen:
            return None
        path = chosen


def main() -> int:
    app = QApplication(sys.argv)

    path = sys.argv[1] if len(sys.argv) > 1 else const.DEFAULT_DATA_PATH
    pipeline = _load_pipeline(app, path)
    if pipeline is None:
        return 1

    from src.controllers.analysis_controller import AnalysisController
    from src.views.main_window import MainWindow

    window = MainWindow()
    AnalysisController(window, pipeline)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
