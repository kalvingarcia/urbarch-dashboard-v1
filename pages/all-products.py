from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFabButton
from api.database import Database
from widgets.datawindow import DataWindow, DataHeader

class AllProducts(MDScreen):
    def __init__(self, **kwargs):
        super(AllProducts, self).__init__(**kwargs)
        self.name = "all-products"

        home = MDIconButton(
            icon = "home",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )
        home.bind(on_press = lambda *args: self._switch("home"))

        self.data_window = DataWindow(
            DataHeader(columns = ["id", "name", "description"]
        ))
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                home,
                MDLabel(text = "All Product", font_style = "Display", role = "small", adaptive_size = True),
                adaptive_height = True,
                spacing = "20dp",
                padding = ['10dp']
            ),
            self.data_window,
            orientation = "vertical",
            adaptive_height = True,
            padding = "10dp",
            pos_hint = {"top": 1}
        ))

        create_product =  MDFabButton(
            icon = "pencil-outline",
            style = "large",
            color_map = "secondary",
            pos_hint = {"right": 1}
        )
        create_product.bind(on_press = lambda *args: self._switch("product"))
        self.add_widget(create_product)

        self.md_bg_color = self.theme_cls.surfaceColor

    def on_pre_enter(self):
        def edit_product(id):
            screen = self.manager.get_screen("product")
            screen.set_id(id)
            self._switch("product")

        self.data_window.update(Database.get_product_list(), lambda data: edit_product(data["id"]) if "id" in data.keys() else self._switch("home"))

