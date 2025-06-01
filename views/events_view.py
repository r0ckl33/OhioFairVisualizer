from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem,
    QMessageBox, QLineEdit, QLabel
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from views.event_dialog import EventDialog
from models.event_model import Event

class EventsView(QWidget):
    event_edited = pyqtSignal()
    def __init__(self, events, event_repo, parent=None):
        super().__init__(parent)
        self.resize(200, 400)
        self.events = events
        self.event_repo = event_repo
        self.filter_text = ""
        self.init_ui()
        self.refresh()

    def init_ui(self):
        self.setWindowTitle('Events')
        layout = QVBoxLayout(self)
        # Filter label and box
        filter_row = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_box = QLineEdit()
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.filter_box, 1)
        layout.addLayout(filter_row)
        self.filter_box.textChanged.connect(self.on_filter_changed)
        # Event list
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.edit_event)
        layout.addWidget(self.list)
        # Add/Delete buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.del_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        layout.addLayout(btn_layout)
        self.add_btn.clicked.connect(self.add_event)
        self.del_btn.clicked.connect(self.delete_event)
        self.setLayout(layout)

    def on_filter_changed(self, text):
        self.filter_text = text
        self.refresh()

    def refresh(self):
        self.list.clear()
        # Sort events by description (case-insensitive)
        filtered = [
            ev for ev in self.events
            if self.filter_text.strip().lower() in ev.description.lower()
        ]
        for ev in sorted(filtered, key=lambda e: e.description.lower()):
            item = QListWidgetItem(f"{ev.description}")
            r, g, b = ev.chip
            item.setBackground(QColor(r, g, b))
            self.list.addItem(item)

    def add_event(self):
        dialog = EventDialog(parent=self)
        if dialog.exec():
            new_event = dialog.get_event()
            self.events.append(new_event)
            self.event_repo.save_events(self.events)
            self.refresh()
            self.event_edited.emit()

    def edit_event(self, item):
        idx = self.list.row(item)
        filtered = [
            ev for ev in self.events
            if self.filter_text.strip().lower() in ev.description.lower()
        ]
        sorted_filtered = sorted(filtered, key=lambda e: e.description.lower())
        ev = sorted_filtered[idx]
        orig_idx = self.events.index(ev)
        dialog = EventDialog(ev, parent=self)
        if dialog.exec():
            self.events[orig_idx] = dialog.get_event()
            self.event_repo.save_events(self.events)
            self.refresh()
            self.event_edited.emit()

    def delete_event(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        filtered = [
            ev for ev in self.events
            if self.filter_text.strip().lower() in ev.description.lower()
        ]
        sorted_filtered = sorted(filtered, key=lambda e: e.description.lower())
        if idx >= len(sorted_filtered):
            return
        ev = sorted_filtered[idx]
        orig_idx = self.events.index(ev)
        confirm = QMessageBox.question(self, "Delete Event", "Delete this event?")
        if confirm == QMessageBox.StandardButton.Yes:
            del self.events[orig_idx]
            self.event_repo.save_events(self.events)
            self.refresh()
            self.event_edited.emit()
