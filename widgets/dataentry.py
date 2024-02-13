from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel

class DataHeader(MDGridLayout):
    def __init__(self, header: list, **kwargs):
        super(DataHeader, self).__init__(**kwargs)

        self.cols = len(header)
        for text in header:
            print(text)
            self.add_widget(MDLabel(text = text))

class DataEntry(MDGridLayout):
    def __init__(self, entry: dict, on_press, **kwargs):
        super(DataEntry, self).__init__(**kwargs)

        self.data = entry
        self._on_press = on_press

        self.cols = len(entry)
        for text in self.data.values():
            self.add_widget(MDLabel(text = text))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._on_press(self.data["id"])
            return True
        return super(DataEntry, self).on_touch_down(touch)

