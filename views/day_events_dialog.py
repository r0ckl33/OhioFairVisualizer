from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from utils.date_utils import parse_date

LEFT_BORDER = "border-top-left-radius: 5px; border-bottom-left-radius: 5px; "
RIGHT_BORDER = "border-top-right-radius: 5px; border-bottom-right-radius: 5px; "

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
            r, g, b = event.chip
            label = QLabel(event.description)
            label.setStyleSheet(
                f"background: rgb({r},{g},{b}); color: #fff; padding:2px 4px; font-size:12px;")
            if day == start:
                label.setStyleSheet(label.styleSheet() + LEFT_BORDER)
            if day == end:
                label.setStyleSheet(label.styleSheet() + RIGHT_BORDER)

            layout.addWidget(label)
        self.setLayout(layout)
