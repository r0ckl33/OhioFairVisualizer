import datetime

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal

class ClickableDayLabel(QLabel):
    clicked = pyqtSignal(datetime.datetime)  # Pass day as int

    def __init__(self, dt, parent=None):
        super().__init__(parent)
        self._date = dt
        self.setText(str(dt.day))

    def mousePressEvent(self, event):
        # print(f"Day label clicked: {self._date}")
        self.clicked.emit(self._date)
        # self.clicked.emit(self._day)
        # super().mousePressEvent(event)
