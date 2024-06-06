from kivymd.uix.screen import MDScreen
from kivymd.theming import ThemableBehavior
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from api.database import Database
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText, MDTextFieldLeadingIcon
from widgets.forms.form import FormStructure, Form, TextInput, SwitchInput, CheckboxInput, CheckGroup
from widgets.forms.overviewforms import TagForm

class CustomForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, on_cancel = None, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)

        self.__old_custom_id = None
        self.__on_submit = on_submit

        self.__form = Form(
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Custom Name"),
                        MDTextFieldHelperText(text = "Example: \"Custom Greek Keys\""),
                        form_id = "name",
                        size_hint_x = 0.6,
                    ),
                    SwitchInput(label = "Display", form_id = "display", size_hint_x = 0.25),
                    adaptive_height = True
                ),
                TextInput(
                    MDTextFieldHintText(text = "Custom Description"),
                    MDTextFieldHelperText(text = "This is not the product overview"),
                    form_id = "description",
                ),
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Product ID"),
                        MDTextFieldHelperText(text = "Example: for \"Custom Greek Keys\", it would be \"_____\""),
                        form_id = "listing_id",
                        size_hint_x = 0.6,
                    ),
                    TextInput(
                        MDTextFieldHintText(text = "Variation Extension"),
                        MDTextFieldHelperText(text = "Example: for \"Custom Greek Keys\", it would be \"_____\""),
                        form_id = "variation_extension",
                        size_hint_x = 0.4,
                    ),
                    adaptive_height = True
                ),
                TextInput(
                    MDTextFieldHintText(text = "Customer Name"),
                    MDTextFieldHelperText(text = "The person or company the custom was made for."),
                    form_id = "customer",
                ),
                adaptive_height = True,
                orientation = "vertical",
                padding = ["20dp", "20dp", "20dp", 0]
            )

        submit = MDIconButton(
            icon = "check",
            style = "filled",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        submit.bind(on_press = lambda *args: self.submit())

        home = MDIconButton(
            icon = "home",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )
        home.bind(on_press = lambda *args: on_cancel())

        self.add_widget(MDBoxLayout(
            home,
            MDLabel(text = "Custom Information", font_style = "Display", role = "small", adaptive_size = True),
            adaptive_height = True,
            spacing = "20dp",
            padding = ['20dp']
        ))
        self.add_widget(self.__form)
        self.add_widget(MDBoxLayout(
            submit,
            padding = ['20dp'],
            adaptive_height = True,
        ))

        self.orientation = "vertical"
        self.adaptive_height = True
        self.pos_hint = {"top": 1}

    def default(self):
        self.__form.default()

    def prefill(self, id):
        self.__old_custom_id = id
        self.__form.prefill(Database.get_custom(self.__old_custom_id))

    def submit(self):
        if self.__old_custom_id:
            Database.update_custom(self.__old_custom_id, self.__form.submit()[1])
            print(self.__form.submit()[1])
        else:
            Database.create_custom(self.__form.submit()[1])
            print(self.__form.submit()[1])
        self.__old_custom_id = None
        if self.__on_submit:
            self.__on_submit()