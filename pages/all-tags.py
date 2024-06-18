from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogContentContainer, MDDialogButtonContainer
from api.database import Database
from widgets.datawindow import DataWindow, DataHeader
from widgets.forms.form import FormStructure, Form, TextInput, DropdownInput
from widgets.forms.createtagform import CreateTagForm

class AllTags(MDScreen):
    def __init__(self, **kwargs):
        super(AllTags, self).__init__(**kwargs)
        self.name = "all-tags"

        self.tag_form = CreateTagForm(on_submit = lambda: self.update())

        home = MDIconButton(
            icon = "home",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )
        home.bind(on_press = lambda *args: self._switch("home"))

        self.data_window = DataWindow(
            DataHeader(columns = ["id", "name", "category"]
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
            orientation = "vertical",
            adaptive_height = True,
            padding = "10dp",
            pos_hint = {"top": 1}
        ))

        create_tag =  MDFabButton(
            icon = "pencil-outline",
            style = "large",
            color_map = "secondary",
            pos_hint = {"right": 0.98, "top": 0.14}
        )
        create_tag.bind(on_press = lambda *args: self.tag_form.default())
        self.add_widget(create_tag)

        self.md_bg_color = self.theme_cls.surfaceColor

    def update(self):
        def edit_tag(id):
            self.tag_form.prefill(id)

        def delete_tag(id):
            cancel = MDIconButton(icon = "window-close")
            confirm = MDIconButton(icon = "check", style = "filled")

            dialog = MDDialog(
                MDDialogHeadlineText(text = "Are you sure you'd like to delete this tag?", halign = "left"),
                MDDialogSupportingText(text = "The data will be lost forever...", halign = "left"),
                MDDialogButtonContainer(
                    MDLabel(text = " "),
                    cancel,
                    confirm,
                    spacing = "10dp",
                )
            )

            def delete():
                Database.delete_tag(id)
                dialog.dismiss()
                self.update()

            cancel.bind(on_press = lambda *args: dialog.dismiss())
            confirm.bind(on_release = lambda *args: delete())

            dialog.open()

        self.data_window.update(
            Database.get_tag_list(),
            lambda data: edit_tag(data["id"]) if "id" in data.keys() else self._switch("home"),
            lambda data: delete_tag(data["id"]) if "id" in data.keys() else self._switch("home")
        )

    def on_pre_enter(self):
        self.update()