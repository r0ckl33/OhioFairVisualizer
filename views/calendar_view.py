from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from utils.clickable_day_label import ClickableDayLabel
from utils.date_utils import parse_date
import calendar
from datetime import datetime, timedelta
from views.day_events_dialog import DayEventsDialog

# Clickable QLabel for '+x more' labels
class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        self.clicked.emit()
        super().mouseReleaseEvent(event)

class CalendarView(QWidget):
    day_clicked  = pyqtSignal(object)

    def __init__(self, events, parent=None):
        super().__init__(parent)
        self.events = events
        self.resize(1000, 800)
        self.today = datetime.today()
        self.current_date = datetime(self.today.year, self.today.month, 1)

        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = None
        self.select_day_events = None

        self.init_ui()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.header = QHBoxLayout()
        self.prev_btn = QPushButton('‹')
        self.next_btn = QPushButton('›')
        self.today_btn = QPushButton('Today')
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header.addWidget(self.prev_btn)
        self.header.addWidget(self.month_label, 1)
        self.header.addWidget(self.next_btn)
        self.header.addWidget(self.today_btn)

        layout.addLayout(self.header)
        self.grid = QGridLayout()
        self.grid.setContentsMargins(2, 2, 2, 2)  # (Optional: compactness)
        layout.addLayout(self.grid)

        self.prev_btn.clicked.connect(self.go_prev)
        self.next_btn.clicked.connect(self.go_next)
        self.today_btn.clicked.connect(self.go_today)

        self.setLayout(layout)

    def go_prev(self):
        prev_month = self.current_date.month - 1 or 12
        prev_year = self.current_date.year - (1 if self.current_date.month == 1 else 0)
        self.current_date = datetime(prev_year, prev_month, 1)
        self.refresh()

    def go_next(self):
        next_month = self.current_date.month + 1 if self.current_date.month < 12 else 1
        next_year = self.current_date.year + (1 if self.current_date.month == 12 else 0)
        self.current_date = datetime(next_year, next_month, 1)
        self.refresh()

    def go_today(self):
        self.current_date = datetime(self.today.year, self.today.month, 1)
        self.refresh()

    def refresh(self):
        calendar.setfirstweekday(calendar.SUNDAY)
        while self.grid.count():
            widget = self.grid.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        # Header row (Sun-Sat)
        days = list(calendar.day_abbr)
        days = days[-1:] + days[:-1]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(label, 0, i)
            # Set the grid layout's row stretch to 0 to prevent extra space
            self.grid.setRowStretch(0, 0)
            # Set size policy to ensure the label doesn't expand unnecessarily
            label.setSizePolicy(
                QSizePolicy.Policy.Preferred,  # Horizontal policy
                QSizePolicy.Policy.Fixed  # Vertical policy - fixed height
            )

        self.grid.setVerticalSpacing(2)  # Reduce space between header and top row
        year, month = self.current_date.year, self.current_date.month
        self.month_label.setText(self.current_date.strftime("%B %Y"))

        first_weekday, days_in_month = calendar.monthrange(year, month)
        offset = (first_weekday + 1) % 7
        grid_start = self.current_date - timedelta(days=offset)
        for week in range(1, 7):
            for day in range(7):
                cell_date = grid_start + timedelta(days=(week - 1) * 7 + day)
                events = self.get_events_for_date(cell_date)
                is_current_month = cell_date.month == month
                self.add_day_cell(cell_date, week, day, events, is_current_month)

    def add_day_cell(self, date, row, col, events, is_current_month):
        cell = QFrame()
        cell.setFrameShape(QFrame.Shape.StyledPanel)
        cell_layout = QVBoxLayout(cell)
        cell_layout.setContentsMargins(2, 2, 2, 2)
        cell_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # cell.setStyleSheet(f"background: rgb(111,11,211); ")
        # day_label = QLabel(str(date.day))
        day_label = ClickableDayLabel(date)
        day_label.clicked.connect(self.on_day_cell_clicked)
        day_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        if not is_current_month:
            day_label.setStyleSheet("color: #aaa;")
        if date.date() == self.today.date():
            day_label.setStyleSheet("color: #0f0f0f; background: #a8c7fa;")
        cell_layout.addWidget(day_label)
        visible = 4
        for i, ev in enumerate(events[:visible]):
            start = parse_date(ev.start_date).date()
            end = parse_date(ev.end_date).date()
            cur = date.date()

            ev_label = QLabel(ev.description)
            r, g, b = ev.chip
            # ev_label.setStyleSheet(
            #     f"background: rgb({r},{g},{b}); color: #fff; border-radius: 5px; padding:1px 2px; font-size:11px; ")
            ev_label.setStyleSheet(
                f"background: rgb({r},{g},{b}); color: #fff; padding:1px 2px; font-size:11px; ")
            if cur == start:
                ev_label.setStyleSheet(ev_label.styleSheet() +
                                       f"border-top-left-radius: 5px; border-bottom-left-radius: 5px; ")
            if cur == end:
                ev_label.setStyleSheet(ev_label.styleSheet() +
                                       f"border-top-right-radius: 5px; border-bottom-right-radius: 5px; ")

            ev_label.setToolTip(f"{ev.description}\n{ev.start_date} – {ev.end_date}")
            ev_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            cell_layout.addWidget(ev_label)
        if len(events) > visible:
            more = len(events) - visible
            more_label = ClickableLabel(f"+{more} more")
            more_label.setStyleSheet("color: #999; font-size:10px; text-decoration: underline;")
            more_label.setCursor(Qt.CursorShape.PointingHandCursor)
            more_label.clicked.connect(lambda _=None, d=date, evs=events: self.show_day_events_dialog(d, evs))
            cell_layout.addWidget(more_label)
        cell.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.grid.addWidget(cell, row, col)

    def show_day_events_dialog(self, date, events):
        dlg = DayEventsDialog(date, events, self)
        dlg.exec()

    def get_events_for_date(self, date):
        result = []
        for e in self.events:
            start = parse_date(e.start_date)
            end = parse_date(e.end_date)
            if start.date() <= date.date() <= end.date():
                result.append(e)
        result.sort(key=lambda e: (parse_date(e.start_date), e.description))
        return result

    def on_day_cell_clicked(self, dt):
        # Print all events whose date range contains dt
        matches = []

        for e in self.events:
            start = datetime.strptime(e.start_date, "%m/%d/%Y").date() if isinstance(e.start_date,
                                                                                              str) else e.start_date
            end = datetime.strptime(e.end_date, "%m/%d/%Y").date() if isinstance(e.end_date,
                                                                                          str) else e.end_date
            if start <= dt.date() <= end:
                matches.append(e)

        # for ev in matches:
        #     print(f"- {ev.description} ({ev.start_date} to {ev.end_date})")

        # de-select events if user selected the same day
        if matches == self.select_day_events:
            matches = []

        self.select_day_events = matches
        self.day_clicked.emit(matches)
        self.refresh()