from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFabButton, MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from api.database import Database
from widgets.datawindow import DataWindow, DataHeader
from widgets.forms.form import Form, TextInput, DropdownInput

class AllTags(MDScreen):
    def __init__(self, **kwargs):
        super(AllTags, self).__init__(**kwargs)
        self.name = "all-tags"

        home = MDIconButton(
            icon = "home",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )
        home.bind(on_press = lambda *args: self._switch("home"))

        create_product =  MDFabButton(
            icon = "pencil-outline",
            style = "large",
            color_map = "secondary",
            pos_hint = {"right": 1}
        )
        create_product.bind(on_press = lambda *args:  self.create_tag())
        self.data_window = DataWindow(
            DataHeader(columns = ["id", "name", "category_id"]
        ))
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                home,
                MDLabel(text = "All Tags", font_style = "Display", role = "small", adaptive_size = True),
                adaptive_height = True,
                spacing = "20dp",
                padding = ['10dp']
            ),
            self.data_window,
            create_product,
            orientation = "vertical",
            adaptive_height = True,
            padding = "10dp",
            pos_hint = {"top": 1}
        ))

        self.md_bg_color = self.theme_cls.surfaceColor

    def on_pre_enter(self):
        self.data_window.update(Database.get_tag_list(), None)

    def create_tag(self):
        categories = [{
            "value": category["id"],
            "text": category["name"]
        } for category in Database.get_tag_categories()]
        tag_form = Form(
            TextInput(form_id = "name"),
            DropdownInput(form_id = "category_id", data = categories),
            orientation = "vertical",
            adaptive_height = True
        )

        def send_tag(data):
            Database.create_tag(data)
            self.data_window.update(Database.get_tag_list(), lambda uaid: self.edit_screen(uaid))

        complete = MDButton(
            MDButtonText(text = "Add Tag")
        )
        complete.bind(on_press = lambda *args: send_tag(tag_form.submit()[1]))

        MDDialog(
            MDDialogHeadlineText(text = "New Tag"),
            MDDialogContentContainer(
                tag_form
            ),
            MDDialogButtonContainer(
                complete
            )
        ).open()