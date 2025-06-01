import json
from datetime import datetime

class Event:
    def __init__(self, description, county, city, independent, visited, start_date, end_date, chip):
        self.description = description
        self.county = county
        self.city = city
        self.independent = independent
        self.visited = visited
        self.start_date = start_date
        self.end_date = end_date
        self.chip = chip

    @staticmethod
    def from_dict(d):
        return Event(
            description=d['description'],
            county=d['county'],
            city=d['city'],
            independent=d['independent'],
            visited=d['visited'],
            start_date=d['start_date'],
            end_date=d['end_date'],
            chip=d['chip']
        )

    def to_dict(self):
        return {
            'description': self.description,
            'county': self.county,
            'city': self.city,
            'independent': self.independent,
            'visited': self.visited,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'chip': self.chip
        }

class EventRepository:
    def __init__(self, path='data/events.json'):
        self.path = path

    def load_events(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            return [Event.from_dict(x) for x in json.load(f)]

    def save_events(self, events):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in events], f, indent=2)
