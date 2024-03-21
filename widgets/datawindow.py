from kivy.core.window import Window
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class DataHeader(MDGridLayout):
    def __init__(self, *args, columns: list, **kwargs):
        super(DataHeader, self).__init__(*args, **kwargs)

        self.cols = len(columns) + 2
        self.columns = columns
        for text in self.columns:
            self.add_widget(MDLabel(text = text, md_bg_color = self.theme_cls.surfaceContainerColor, padding = "10dp"))
        self.add_widget(MDLabel(text = " ", md_bg_color = self.theme_cls.surfaceContainerColor, size_hint_x = None, width = "40dp"))
        self.add_widget(MDLabel(text = " ", md_bg_color = self.theme_cls.surfaceContainerColor, size_hint_x = None, width = "40dp"))

        self.adaptive_height = True
        self.spacing = "5dp"

class DataEntry(MDGridLayout):
    def __init__(self, entry: dict, *args, on_press = None, on_delete = None, **kwargs):
        super(DataEntry, self).__init__(**kwargs)

        self.data = entry

        self.cols = len(entry) + 2
        for text in self.data.values():
            self.add_widget(MDLabel(text = str(text), md_bg_color = self.theme_cls.surfaceContainerLowColor, padding = "10dp"))
        edit = MDIconButton(icon = "pencil")
        edit.bind(on_release = lambda *args: on_press(self.data))
        self.add_widget(edit)
        delete = MDIconButton(icon = "window-close")
        delete.bind(on_release = lambda *args: on_delete(self.data))
        self.add_widget(delete)

        self.adaptive_height = True
        self.spacing = "5dp"

class DataWindow(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        self.__header = None
        super(DataWindow, self).__init__(*args, **kwargs)

        self.adaptive_height = True
        self.md_bg_color = self.theme_cls.surfaceColor
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.padding = "5dp"

        Window.bind(on_resize = self._on_window_resize)

    def _on_window_resize(self, window, width, height):
        self.__layout.parent.height = height - (1600 - 1300)

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
                size_hint_y = None
            )) 

    def update(self, data: list[dict], on_data_press = None, on_delete_item = None):
        self.__layout.clear_widgets()
        if len(data) > 0:
            data = [{column: entry[column] for column in self.__header.columns} for entry in data]
            for entry in data:
                self.__layout.add_widget(DataEntry(entry, on_press = on_data_press, on_delete = on_delete_item))
