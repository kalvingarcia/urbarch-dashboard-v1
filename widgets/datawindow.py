from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel

class DataHeader(MDGridLayout):
    def __init__(self, *args, columns: list, **kwargs):
        super(DataHeader, self).__init__(*args, **kwargs)

        self.cols = len(columns)
        self.columns = columns
        for text in self.columns:
            self.add_widget(MDLabel(text = text, md_bg_color = self.theme_cls.surfaceContainerColor, padding = "10dp"))

        self.adaptive_height = True
        self.spacing = "5dp"

class DataEntry(MDGridLayout):
    def __init__(self, entry: dict, *args, on_press = None, **kwargs):
        super(DataEntry, self).__init__(**kwargs)

        self.data = entry
        self._on_press = on_press

        self.cols = len(entry)
        for text in self.data.values():
            self.add_widget(MDLabel(text = str(text), md_bg_color = self.theme_cls.surfaceContainerLowColor, padding = "10dp"))

        self.adaptive_height = True
        self.spacing = "5dp"

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self._on_press:
                self._on_press(self.data)
            return True
        return super(DataEntry, self).on_touch_down(touch)

class DataWindow(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        self.__header = None
        super(DataWindow, self).__init__(*args, **kwargs)

        self.adaptive_height = True
        self.md_bg_color = self.theme_cls.surfaceColor
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.padding = "5dp"

        # if not self.__header:
        #     raise Exception()

    def add_widget(self, widget):
        if isinstance(widget, DataHeader):
            self.__header = widget
            super(DataWindow, self).add_widget(widget)
            self.__layout = MDBoxLayout(
                orientation = "vertical",
                adaptive_height = True,
                spacing = "5dp"
            )
            return super(DataWindow, self).add_widget(MDScrollView(
                self.__layout,
                size_hint_y = None,
                height = "650dp"
            )) 

    def update(self, data: list[dict], on_data_press = None):
        self.__layout.clear_widgets()
        if len(data) > 0:
            data = [{column: entry[column] for column in self.__header.columns} for entry in data]
            for entry in data:
                self.__layout.add_widget(DataEntry(entry, on_press = on_data_press))
