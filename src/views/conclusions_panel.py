from __future__ import annotations

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class ConclusionsPanel(QWidget):
    """Read-only text box with automatically generated conclusions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumHeight(120)
        self.text_edit.setPlaceholderText("Tu pojawią się wnioski z analizy...")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)

    def set_text(self, text: str) -> None:
        """Set the conclusions text."""
        self.text_edit.setPlainText(text)
