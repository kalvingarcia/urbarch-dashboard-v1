from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

from .dataentry import DataEntry, DataHeader

class DataWindow(MDScrollView):
    def __init__(self, *args, **kwargs):
        super(DataWindow, self).__init__(*args, **kwargs)

        self.layout = MDBoxLayout(orientation = "vertical", size_hint_y = None)
        self.add_widget(self.layout)

    def _create_labels(self, data: list[dict], on_data_press):
        if len(data) > 0:
            self.layout.add_widget(DataHeader(data[0].keys()))
            for point in data:
                self.layout.add_widget(DataEntry(point, on_data_press))

    def update(self, data: list[dict], on_data_press):
        self.layout.clear_widgets()
        self._create_labels(data, on_data_press)
