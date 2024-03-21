from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from api.database import Database
from widgets.datawindow import DataWindow, DataHeader

class AllSalvage(MDScreen):
    def __init__(self, **kwargs):
        super(AllSalvage, self).__init__(**kwargs)
        self.name = "all-salvage"

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
                MDLabel(text = "All Salvage", font_style = "Display", role = "small", adaptive_size = True),
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

        create_salvage =  MDFabButton(
            icon = "pencil-outline",
            style = "large",
            color_map = "secondary",
            pos_hint = {"right": 0.98, "top": 0.14}
        )
        create_salvage.bind(on_press = lambda *args: self._switch("salvage"))
        self.add_widget(create_salvage)

        self.md_bg_color = self.theme_cls.surfaceColor

    def on_pre_enter(self):
        def edit_salvage(id):
            screen = self.manager.get_screen("salvage")
            screen.set_id(id)
            self._switch("salvage")

        def delete_salvage(id):
            cancel = MDIconButton(icon = "window-close")
            confirm = MDIconButton(icon = "check", style = "filled")

            dialog = MDDialog(
                MDDialogHeadlineText(text = "Are you sure you'd like to delete this salvage?", halign = "left"),
                MDDialogSupportingText(text = "The data will be lost forever...", halign = "left"),
                MDDialogButtonContainer(
                    MDLabel(text = " "),
                    cancel,
                    confirm,
                    spacing = "10dp",
                )
            )

            def delete():
                Database.delete_salvage(id)
                dialog.dismiss()
                update()

            cancel.bind(on_press = lambda *args: dialog.dismiss())
            confirm.bind(on_release = lambda *args: delete())

            dialog.open()

        def update():
            self.data_window.update(
                Database.get_salvage_list(), 
                lambda data: edit_salvage(data["id"]) if "id" in data.keys() else self._switch("home"),
                lambda data: delete_salvage(data["id"]) if "id" in data.keys() else self._switch("home")
            )

        update()