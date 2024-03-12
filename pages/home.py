from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

class Home(MDScreen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.name = "home"

        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                MDLabel(
                    text = "Welcome to UrbanDash!",
                    bold = True,
                    font_style = "Headline"
                ),
                size_hint_y = 0.2
            ),
            MDBoxLayout(
                MDBoxLayout(
                    MDBoxLayout(
                        MDLabel(text = "Catalog Management", bold = True, adaptive_size = True),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "See All Products",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.25,
                            on_release = lambda *args: self._switch("all-products"),
                            ripple_behavior = True
                        ),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "Create New Product",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.5,
                            on_release = lambda *args: self._switch("product"),
                            ripple_behavior = True
                        ),
                        MDBoxLayout(
                            MDCard(
                                MDRelativeLayout(
                                    MDLabel(
                                        text = "Add New Salvage",
                                        pos = ["12dp", "12dp"],
                                        adaptive_height = True
                                    ),
                                ),
                                on_release = lambda *args: self._switch("salvage"),
                                ripple_behavior = True
                            ),
                            MDCard(
                                MDRelativeLayout(
                                    MDLabel(
                                        text = "Add Stock",
                                        pos = ["12dp", "12dp"],
                                        adaptive_height = True
                                    ),
                                ),
                                on_release = lambda *args: self._switch("stock"),
                                ripple_behavior = True
                            ),
                            spacing = '20dp',
                            size_hint_y = 0.25,
                        ),
                        size_hint_x = .25,
                        orientation = "vertical",
                        spacing = '20dp'
                    ),
                    MDBoxLayout(
                        MDLabel(text = " ", adaptive_size = True),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "See All Salvage",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.25,
                            on_release = lambda *args: self._switch("all-salvage"),
                            ripple_behavior = True
                        ),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "See All Stock",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.25,
                            on_release = lambda *args: self._switch("all-stock"),
                            ripple_behavior = True
                        ),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "See All Tags",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            on_release = lambda *args: self._switch("all-tags"),
                            ripple_behavior = True,
                            size_hint_y = 0.5,
                        ),
                        size_hint_x = .25,
                        orientation = "vertical",
                        spacing = '20dp'
                    ),
                    MDBoxLayout(
                        MDLabel(text = "Gallery Management", bold = True, adaptive_size = True),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "Add New Custom",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.5,
                            on_release = lambda *args: self._switch("custom"),
                            ripple_behavior = True
                        ),
                        MDCard(
                            MDRelativeLayout(
                                MDLabel(
                                    text = "See All Custom",
                                    pos = ["12dp", "12dp"],
                                    adaptive_height = True
                                ),
                            ),
                            size_hint_y = 0.25,
                            on_release = lambda *args: self._switch("all-custom"),
                            ripple_behavior = True
                        ),
                        MDLabel(size_hint_y = 0.25,),
                        # MDCard(
                        #     MDRelativeLayout(
                        #         MDLabel(
                        #             text = "",
                        #             pos = ["12dp", "12dp"],
                        #             adaptive_height = True
                        #         ),
                        #     ),
                        #     on_release = lambda *args: self._switch("all-tags"),
                        #     ripple_behavior = True,
                        #     size_hint_y = 0.25,
                        # ),
                        size_hint_x = .25,
                        orientation = "vertical",
                        spacing = '20dp'
                    ),
                    MDLabel(size_hint_x = .25,),
                    spacing = '20dp'
                ),
            ),
            orientation = "vertical",
            padding = ['20dp']
        ))


