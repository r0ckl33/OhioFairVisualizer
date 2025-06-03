import os
import geopandas as gpd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip
from PyQt6.QtCore import Qt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.colors import LinearSegmentedColormap
from PyQt6.QtGui import QCursor
import numpy as np
import re
from datetime import datetime

# OHIO_COUNTY_SEATS = {
#     "ADAMS": "WEST UNION", "ALLEN": "LIMA", "ASHLAND": "ASHLAND", "ASHTABULA": "JEFFERSON",
#     # ... (rest of county seats as in previous code) ...
#     "WYANDOT": "UPPER SANDUSKY"
# }

OHIO_COUNTY_SEATS = {
    "FRANKLIN": "COLUMBUS"
}

class MapView(QWidget):
    def __init__(self, events, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map")
        self.resize(800, 800)
        self.events = events

        layout = QVBoxLayout(self)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax.set_aspect("equal")
        self.fig.subplots_adjust(left=0.04, right=0.98, top=0.97, bottom=0.03)

        self.selected_events = []
        self.city_pin_artists = []
        self.city_pin_data = []
        self.press_event = None
        self.orig_xlim = None
        self.orig_ylim = None
        self.plot_map()

        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        # Remove pick event; use hover for tooltip
        self.canvas.mpl_connect("motion_notify_event", self.on_motion_hover)

    def highlight_date(self, events):
        """Update map for selected date (datetime.date)."""
        for ev in events:
            print(f"- {ev.description} ({ev.start_date} to {ev.end_date})")
        self.selected_events = events
        print("plot_map")
        self.plot_map()

    def plot_map(self):
        self.ax.clear()
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tiger_dir = os.path.join(root, "TIGER")
        gdf_counties = gpd.read_file(os.path.join(tiger_dir, "cb_2024_us_county_500k.shp"))
        ohio_counties = gdf_counties[gdf_counties["STATEFP"] == "39"]
        ohio_boundary = ohio_counties.unary_union
        NEUTRAL = (220/255, 220/255, 220/255)
        # selected_dt = self.selected_date
        county_event_map = {}
        for e in self.selected_events:
            county = e.county.strip().upper()
            if county not in county_event_map:
                county_event_map[county] = []
            county_event_map[county].append(tuple(e.chip))

        for _, row in ohio_counties.iterrows():
            county_name = row["NAME"].upper()
            geom = row["geometry"]
            chips = county_event_map.get(county_name, None)
            polygons = []
            if geom.geom_type == "Polygon":
                polygons = [geom]
            elif geom.geom_type == "MultiPolygon":
                polygons = list(geom.geoms)
            else:
                continue
            for poly in polygons:
                if chips:
                    if len(chips) == 1:
                        color = np.array(chips[0]) / 255.0
                        exterior_coords = np.array(poly.exterior.coords)
                        path = Path(exterior_coords)
                        patch = PathPatch(path, facecolor=color, edgecolor="black", linewidth=0.8, zorder=1)
                        self.ax.add_patch(patch)
                        for interior in poly.interiors:
                            interior_coords = np.array(interior.coords)
                            interior_path = Path(interior_coords)
                            interior_patch = PathPatch(
                                interior_path,
                                facecolor="white", edgecolor="black", linewidth=0.8, zorder=1)
                            self.ax.add_patch(interior_patch)
                    else:
                        try:
                            n = len(chips)
                            colors = [np.array(c)/255.0 for c in chips]
                            cm = LinearSegmentedColormap.from_list("countygrad", colors)
                            xs, ys = poly.exterior.xy
                            xmin, xmax = min(xs), max(xs)
                            ymin, ymax = min(ys), max(ys)
                            y_grid = np.linspace(ymin, ymax, 100)
                            for j in range(len(y_grid)-1):
                                y0, y1 = y_grid[j], y_grid[j+1]
                                color = cm(j / (len(y_grid)-1))
                                box = gpd.GeoSeries.box(xmin, y0, xmax, y1)
                                inter = poly.intersection(box[0])
                                if not inter.is_empty and inter.geom_type == "Polygon":
                                    ex_coords = np.array(inter.exterior.coords)
                                    path = Path(ex_coords)
                                    patch = PathPatch(path, facecolor=color, edgecolor="none", linewidth=0, zorder=1)
                                    self.ax.add_patch(patch)
                            exterior_coords = np.array(poly.exterior.coords)
                            self.ax.plot(exterior_coords[:, 0], exterior_coords[:, 1], color="black", linewidth=0.8, zorder=2)
                        except Exception as ex:
                            avg_color = tuple(np.mean(colors, axis=0))
                            exterior_coords = np.array(poly.exterior.coords)
                            path = Path(exterior_coords)
                            patch = PathPatch(path, facecolor=avg_color, edgecolor="black", linewidth=0.8, zorder=1)
                            self.ax.add_patch(patch)
                else:
                    exterior_coords = np.array(poly.exterior.coords)
                    path = Path(exterior_coords)
                    patch = PathPatch(path, facecolor=NEUTRAL, edgecolor="black", linewidth=0.8, zorder=1)
                    self.ax.add_patch(patch)
                    for interior in poly.interiors:
                        interior_coords = np.array(interior.coords)
                        interior_path = Path(interior_coords)
                        interior_patch = PathPatch(
                            interior_path,
                            facecolor="white", edgecolor="black", linewidth=0.8, zorder=1)
                        self.ax.add_patch(interior_patch)
                exterior_coords = np.array(poly.exterior.coords)
                self.ax.plot(exterior_coords[:, 0], exterior_coords[:, 1], color="black", linewidth=0.8, zorder=2)
            centroid = row["geometry"].centroid
            self.ax.text(
                centroid.x, centroid.y, row["NAME"].title(), fontsize=7, ha="center", va="center", color="#333",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7), zorder=10
            )

        # Cities -- only inside Ohio
        places_gdf = gpd.read_file(os.path.join(tiger_dir, "tl_2024_39_place.shp"))
        ohio_cities = places_gdf[places_gdf.intersects(ohio_boundary)]
        event_cities = {e.city.strip().upper(): [] for e in self.events}
        for e in self.events:
            event_cities[e.city.strip().upper()].append(e)
        city_name_map = {}
        for _, row in ohio_cities.iterrows():
            raw_name = row["NAME"].upper()

            if "Saint Joseph".upper() in raw_name:
                print(raw_name)
            raw_name = re.sub(r" \(.*\)", "", raw_name)
            raw_name = re.sub(r"MOUNT ", "MT. ", raw_name)
            if "Saint Joseph".upper() in raw_name:
                print(raw_name)

            for suffix in [" CITY", " VILLAGE", " TOWN", " ", " CORP", " CORPORATION"]:
                if raw_name.endswith(suffix):
                    raw_name = raw_name[: -len(suffix)]
            city_name_map[raw_name] = row

        self.city_pin_artists = []
        self.city_pin_data = []
        for county, seat in OHIO_COUNTY_SEATS.items():
            OHIO_COUNTY_SEATS[county] = seat.upper()
        for city, evlist in event_cities.items():
            city_key = city
            found_row = None
            for cand in [city_key, city_key.replace(" CITY", ""), city_key.replace(" VILLAGE", "")]:
                if cand in city_name_map:
                    found_row = city_name_map[cand]
                    break
            if found_row is None:
                continue
            x, y = found_row["geometry"].centroid.xy
            is_capital = any(seat == city_key for seat in OHIO_COUNTY_SEATS.values())
            pin_color = "#28a745" if all(ev.visited for ev in evlist) else "#d32f2f"

            # marker = "*" if is_capital else "o"
            # size = 11 if is_capital else 6
            # matplotlib markers = P: plus, D: diamond, p: pentagon
            is_independent = any(ev.independent == True for ev in evlist)
            marker = "*" if is_capital else ("P" if is_independent else "o")
            size = 11 if is_capital else (7 if is_independent else 6)

            is_visited = any(ev.visited == True for ev in evlist)
            if is_visited:
                marker = "X"
                size = 7

            artist = self.ax.plot(x[0], y[0], marker=marker, color=pin_color, markersize=size,
                                  markeredgecolor="white", zorder=99)[0]  # <-- zorder high
            self.city_pin_artists.append(artist)
            # City label right of pin
            self.ax.text(
                x[0]+7000, y[0], city.title(), fontsize=7, ha="left", va="center", color="#222",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.5), zorder=100
            )
            event_text = ""
            for ev in evlist:
                event_text += f"{ev.description}\n{ev.start_date} – {ev.end_date}\n"
            self.city_pin_data.append({
                "artist": artist,
                "city": city,
                "x": x[0], "y": y[0],
                "events": evlist,
                "info": event_text
            })

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_frame_on(False)
        self.ax.set_title("")
        self.ax.axis("off")
        self.canvas.draw()

    def on_motion_hover(self, event):
        if not event.inaxes or event.x is None or event.y is None:
            QToolTip.hideText()
            return
        mouse_xy = np.array([event.x, event.y])  # mouse pixel position
        for city_data in self.city_pin_data:
            # Convert data coordinates to display/pixel coordinates
            pin_disp = self.ax.transData.transform((city_data['x'], city_data['y']))
            dist = np.linalg.norm(mouse_xy - pin_disp)
            if dist < 12:  # Only trigger tooltip if mouse is within 12 pixels of pin
                events = city_data['events']
                info = f"{city_data['city'].title()}\n\n"
                for ev in events:
                    info += f"{ev.description}\n{ev.start_date} – {ev.end_date}\nVisited: {'Yes' if ev.visited else 'No'}\n\n"
                QToolTip.showText(QCursor.pos(), info.strip(), self)
                return
        QToolTip.hideText()

    # --- rest unchanged ---
    def on_press(self, event):
        if event.button == 1 and event.inaxes:
            self.press_event = event
            self.orig_xlim = self.ax.get_xlim()
            self.orig_ylim = self.ax.get_ylim()

    def on_release(self, event):
        self.press_event = None

    def on_motion(self, event):
        if self.press_event and event.inaxes:
            dx = event.xdata - self.press_event.xdata
            dy = event.ydata - self.press_event.ydata
            x0, x1 = self.orig_xlim
            y0, y1 = self.orig_ylim
            self.ax.set_xlim(x0 - dx, x1 - dx)
            self.ax.set_ylim(y0 - dy, y1 - dy)
            self.canvas.draw_idle()

    def on_scroll(self, event):
        if event.inaxes:
            scale = 1.2 if event.button == 'up' else (1/1.2)
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            xdata, ydata = event.xdata, event.ydata
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
            self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
            self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
            self.canvas.draw_idle()
