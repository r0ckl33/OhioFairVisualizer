from PyQt6.QtWidgets import QMainWindow, QApplication
from models.event_model import EventRepository
from views.calendar_view import CalendarView
from views.events_view import EventsView
from views.map_view import MapView

class MainController:
    def __init__(self):
        self.event_repo = EventRepository()
        self.events = self.event_repo.load_events()
        self.cal_win = CalendarView(self.events)
        self.ev_win = EventsView(self.events, self.event_repo)
        self.map_win = MapView(self.events)
        self.ev_win.event_edited.connect(self.on_events_changed)

        # self.map_win.day_clicked.connect(self.cal_win.on_day_cell_clicked)
        self.cal_win.day_clicked.connect(self.map_win.highlight_date)

    def show_all_windows(self):
        self.cal_win.setWindowTitle('Calendar')
        self.cal_win.show()
        # Now position map & events relative to calendar
        cal_geom = self.cal_win.geometry()
        # Map: right of calendar +5px
        self.map_win.setWindowTitle('Map')
        self.map_win.move(cal_geom.x() + cal_geom.width() + 5, cal_geom.y())
        self.map_win.show()
        # Events: left of calendar - width - 5px
        self.ev_win.setWindowTitle('Events')
        self.ev_win.move(cal_geom.x() - self.ev_win.width() - 5, cal_geom.y())
        self.ev_win.show()

    def on_events_changed(self):
        self.events = self.event_repo.load_events()
        self.cal_win.events = self.events
        self.cal_win.refresh()
