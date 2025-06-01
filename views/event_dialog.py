from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QCheckBox, QColorDialog, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.event_model import Event
from utils.date_utils import parse_date, format_date
from datetime import datetime

GOOGLE_EVENT_COLORS = [
    (26, 115, 232),   # Google Blue
    (219, 68, 55),    # Google Red
    (244, 180, 0),    # Google Yellow/Orange
    (15, 157, 88),    # Google Green
    (171, 71, 188),   # Google Purple
    (0, 172, 193),    # Google Cyan
    (255, 112, 67),   # Google Deep Orange
    (158, 157, 36),   # Olive/Chartreuse
]

_last_color_index = [0]  # Mutable container to keep index across dialog calls

# Helper to cycle through event colors
def get_next_google_color():
    idx = _last_color_index[0]
    color = GOOGLE_EVENT_COLORS[idx]
    _last_color_index[0] = (idx + 1) % len(GOOGLE_EVENT_COLORS)
    return color


class EventDialog(QDialog):
    def __init__(self, event=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Event' if event else 'Add Event')
        self.event = event
        # self.chip_color = QColor(100, 100, 100)
        if self.event:
            # Use existing chip color for editing
            self.chip_color = QColor(*self.event.chip)
        else:
            # For new event, use the next Google Calendar color
            self.chip_color = QColor(*get_next_google_color())
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.desc = QLineEdit(self.event.description if self.event else "")
        self.county = QLineEdit(self.event.county if self.event else "")
        self.city = QLineEdit(self.event.city if self.event else "")
        self.indep = QCheckBox()
        self.indep.setChecked(self.event.independent if self.event else False)
        self.visited = QCheckBox()
        self.visited.setChecked(self.event.visited if self.event else False)
        self.start = QDateEdit()
        self.start.setCalendarPopup(True)
        self.end = QDateEdit()
        self.end.setCalendarPopup(True)
        if self.event:
            s = parse_date(self.event.start_date)
            e = parse_date(self.event.end_date)
            self.start.setDate(s.date())
            self.end.setDate(e.date())
            self.chip_color = QColor(*self.event.chip)
        else:
            today = datetime.today().date()
            self.start.setDate(today)
            self.end.setDate(today)
        self.chip_btn = QPushButton()
        self.update_chip_btn()
        self.chip_btn.clicked.connect(self.select_chip)
        layout.addRow("Description", self.desc)
        layout.addRow("Start Date", self.start)
        layout.addRow("End Date", self.end)
        layout.addRow("County", self.county)
        layout.addRow("City", self.city)
        layout.addRow("Independent", self.indep)
        layout.addRow("Visited", self.visited)
        layout.addRow("Chip", self.chip_btn)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def update_chip_btn(self):
        rgb = self.chip_color.getRgb()[:3]
        self.chip_btn.setStyleSheet(f"background: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); color: #fff;")
        self.chip_btn.setText(f"{rgb}")

    def select_chip(self):
        color = QColorDialog.getColor(self.chip_color, self, "Select Chip Color")
        if color.isValid():
            self.chip_color = color
            self.update_chip_btn()

    def get_event(self):
        return Event(
            self.desc.text(),
            self.county.text(),
            self.city.text(),
            self.indep.isChecked(),
            self.visited.isChecked(),
            self.start.date().toString("M/d/yyyy"),
            self.end.date().toString("M/d/yyyy"),
            list(self.chip_color.getRgb()[:3])
        )
