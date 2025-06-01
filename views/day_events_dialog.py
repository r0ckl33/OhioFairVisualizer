from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from utils.date_utils import parse_date

class DayEventsDialog(QDialog):
    def __init__(self, day_date, events, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Events on this day")
        layout = QVBoxLayout(self)
        # Centered Day Name and Date
        day_name = day_date.strftime("%A")
        day_number = day_date.strftime("%B %d")
        name_lbl = QLabel(day_name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)
        num_lbl = QLabel(day_number)
        num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(num_lbl)
        # Events
        for event in events:
            start = parse_date(event.start_date).date()
            end = parse_date(event.end_date).date()
            day = day_date.date()
            start_cap = ""
            end_cap = ""
            if day == start and day == end:
                start_cap = "\u25C0 " # ◀
                end_cap = " \u25B6"   # ▶
            elif day == start:
                start_cap = "\u25C0 "       # ◀
            elif day == end:
                end_cap = " \u25B6"         # ▶
            label = QLabel(f"{start_cap}{event.description}{end_cap}")
            r, g, b = event.chip
            label.setStyleSheet(f"background: rgb({r},{g},{b}); color: #fff; border-radius: 5px; padding:2px 4px; font-size:12px;")
            layout.addWidget(label)
        self.setLayout(layout)
