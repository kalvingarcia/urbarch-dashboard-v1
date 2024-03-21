from kivymd.uix.screen import MDScreen
from kivymd.theming import ThemableBehavior
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from api.database import Database
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText, MDTextFieldLeadingIcon
from widgets.forms.form import FormStructure, Form, TextInput, NumberInput, SwitchInput, CheckboxInput, CheckGroup, TabForm
from widgets.forms.overviewforms import TagForm

class ItemForm(FormStructure, MDScrollView, ThemableBehavior):
    __item_number = 0

    @classmethod
    def change_item_number(cls, number):
        cls.__item_number = number

    @classmethod
    def get_item_number(cls):
        return cls.__item_number

    def __init__(self, *args, tab_form_instance = None, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        self.default_name = "New Item"

        def set_item_number(text):
            if text == '':
                text = "New Item"
            else:
                self.__item_number = int(text)
                self.rename_tab(f"Item {self.__item_number}")

        self.__form  = Form(
            Form(
                Form(
                    NumberInput(
                        MDTextFieldHintText(text = "Item Number"),
                        MDTextFieldHelperText(text = "This is the number of the item in the series."),
                        form_id = "serial",
                        is_int = True,
                        on_text_change = set_item_number,
                    ),
                    SwitchInput(label = "Display", form_id = "display"),
                    adaptive_height = True
                ),
                MDLabel(text = "Tags", adaptive_size = True),
                TagForm(),
                orientation = "vertical",
                pos_hint = {"top": 1},
                adaptive_height = True
            ),
            Form(
                TextInput(
                    MDTextFieldHintText(text = "Item Notes"),
                    MDTextFieldHelperText(text = "Any additional information that needs to be included."),
                    form_id = "notes"
                ),
                adaptive_height = True,
                pos_hint = {"top": 1},
                orientation = "vertical"
            ),
            adaptive_height = True,
            padding = ['20dp', '30dp'],
        )
        self.add_widget(self.__form)

        self.md_bg_color = self.theme_cls.surfaceBrightColor

    def prefill(self, data):
        overview = data.pop("overview")
        data.update(overview)

        ItemForm.change_item_number(self.__item_number + 1)

        self.__form.prefill(data)

    def submit(self):
        form_data = self.__form.submit()[1]

        overview = {}
        for key in ["notes"]:
            overview[key] = form_data.pop(key)
        form_data["overview"] = overview

        return "__variation", form_data

    def rename_tab(self, text):
        if hasattr(self, "tab_item"):
            self.tab_item.rename(text)

class StockForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, on_cancel = None, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)

        self.__old_stock_id = None
        self.__on_submit = on_submit

        self.item_number = 1

        item_forms = TabForm(form_id = "items", slide = ItemForm)

        self.__form = Form(
                Form(
                    Form(
                        TextInput(
                            MDTextFieldLeadingIcon(icon = "currency-usd"),
                            MDTextFieldHintText(text = "Stock Price"),
                            MDTextFieldHelperText(text = "Example: for \"Instock Greek Keys\", it would be \"_____\""),
                            form_id = "price"
                        ),
                        SwitchInput(label = "On Sale", form_id = "sale", size_hint_x = 0.4),
                        adaptive_height = True
                    ),
                    Form(
                        TextInput(
                            MDTextFieldHintText(text = "Product ID"),
                            MDTextFieldHelperText(text = "Example: for \"Instock Greek Keys\", it would be \"_____\""),
                            form_id = "product_id",
                            size_hint_x = 0.6,
                        ),
                        TextInput(
                            MDTextFieldHintText(text = "Variation Extension"),
                            MDTextFieldHelperText(text = "Example: for \"Instock Greek Keys\", it would be \"_____\""),
                            form_id = "variation_extension",
                            size_hint_x = 0.6,
                        ),
                        adaptive_height = True
                    ),
                    orientation = "vertical",
                    adaptive_height = True,
                    padding = ["20dp", "20dp", "20dp", 0]
                ),
                item_forms,
                orientation = "vertical",
                adaptive_height = True
        )

        def add_item_form():
            ItemForm.change_item_number(self.item_number)
            item_forms.add_tab()
            self.item_number += 1

        def remove_item_form():
            if item_forms.remove_tab():
                self.item_number -= 1
                ItemForm.change_item_number(self.item_number)

        add_tab = MDIconButton(
            icon = "plus",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        add_tab.bind(on_press = lambda *args: add_item_form())
        remove_tab = MDIconButton(
            icon = "minus",
            style = "outlined",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        remove_tab.bind(on_press = lambda *args: remove_item_form())
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
            MDLabel(text = "Stock Information", font_style = "Display", role = "small", adaptive_size = True),
            adaptive_height = True,
            spacing = "20dp",
            padding = ['20dp']
        ))
        self.add_widget(self.__form)
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                add_tab,
                remove_tab,
                adaptive_height = True,
                spacing = "10dp",
                size_hint_x = 0.5
            ),
            submit,
            padding = ['20dp'],
            adaptive_height = True,
        ))

        self.orientation = "vertical"
        self.adaptive_height = True

    def __reset(self):
        self.item_number = 1

    def default(self):
        self.__reset()
        self.__form.default()

    def prefill(self, id):
        self.__reset()
        self.__old_stock_id = id
        self.__form.prefill(Database.get_stock(self.__old_stock_id))

        self.item_number = ItemForm.get_item_number()

    def submit(self):
        if self.__old_stock_id:
            Database.update_stock(self.__old_stock_id, self.__form.submit()[1])
            print(self.__form.submit()[1])
        else:
            Database.create_stock(self.__form.submit()[1])
            print(self.__form.submit()[1])
        self.__old_stock_id = None
        if self.__on_submit:
            self.__on_submit()