from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText

class Home(MDScreen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.name = "home"

        self.add_widget(MDBoxLayout(
            MDButton(
                MDButtonText(text = "See All Products"),
                style = "filled",
                pos_hint = {"center_x": 0.5, "center_y": 0.5},
                on_touch_down = lambda x, y: self._switch("all-products")
            ),
            MDButton(
                MDButtonText(text = "Add New Product"),
                style = "tonal",
                pos_hint = {"center_x": 0.5, "center_y": 0.5},
                on_touch_down = lambda x, y: self._switch("create-product")
            ),
            orientation = "vertical",
            adaptive_size = True,
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        ))

    def _switch(self, screen: str):
        self.manager.current = screen


