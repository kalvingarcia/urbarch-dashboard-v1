from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextFieldHelperText, MDTextFieldHintText, MDTextFieldLeadingIcon
from kivymd.uix.button import MDIconButton
from api.database import Database
from widgets.forms.form import FormStructure, Form, TextInput, CheckboxInput, CheckGroup, SwitchInput, TabForm, NumberInput, DropdownInput
from widgets.forms.overviewforms import ReplacementForm, TagForm, FinishesForm, OptionsForm

class VariationForm(FormStructure, MDScrollView, ThemableBehavior):
    __variation_number = 0

    @classmethod
    def change_variation_number(cls, number):
        cls.__variation_number = number

    @classmethod
    def get_variation_number(cls):
        return cls.__variation_number

    def __init__(self, *args, **kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)

        self.default_name = f"Variation {self.__variation_number}"

        self.__form = Form(
            Form(
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Variant Name"),
                        MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"ADA\""),
                        on_text_change = self.rename_tab,
                        form_id = "subname"
                    ),
                    SwitchInput(label = "Featured", form_id = "featured", size_hint_x = 0.25),
                    adaptive_height = True
                ),
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Variation Extension"),
                        MDTextFieldHelperText(text = "Example: for \"UA0040-A\", it would be \"A\""),
                        form_id = "extension",
                    ),
                    SwitchInput(label = "Display", form_id = "display", size_hint_x = 0.25),
                    adaptive_height = True
                ),
                NumberInput(
                    MDTextFieldLeadingIcon(icon = "currency-usd"),
                    MDTextFieldHintText(text = "Variation Base Price"),
                    MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"1095\""),
                    form_id = "price",
                    is_int = True
                ),
                MDLabel(text = "Tags", adaptive_size = True),
                TagForm(),
                MDLabel(text = "Finishes", adaptive_size = True),
                FinishesForm(),
                OptionsForm(),
                orientation = "vertical",
                size_hint_x = 0.5,
                adaptive_height = True,
                pos_hint = {"top": 1}
            ),
            Form(
                MDLabel(text = "Specifications", adaptive_size = True),
                Form(
                    Form(
                        NumberInput(
                            MDTextFieldHintText(text = "Variation Height"),
                            form_id = "measurement"
                        ),
                        DropdownInput(
                            data = [
                                {"value": "inches", "text": "in"},
                                {"value": "feet", "text": "ft"},
                                {"value": "milimeters", "text": "mm"},
                                {"value": "centimeters", "text": "cm"}
                            ],
                            form_id = "unit"
                        ),
                        form_id = "height",
                        adaptive_height = True
                    ),
                    Form(
                        NumberInput(
                            MDTextFieldHintText(text = "Variation Width"),
                            form_id = "measurement"
                        ),
                        DropdownInput(
                            data = [
                                {"value": "inches", "text": "in"},
                                {"value": "feet", "text": "ft"},
                                {"value": "milimeters", "text": "mm"},
                                {"value": "centimeters", "text": "cm"}
                            ],
                            form_id = "unit"
                        ),
                        form_id = "width",
                        adaptive_height = True
                    ),
                    Form(
                        NumberInput(
                            MDTextFieldHintText(text = "Variation Depth"),
                            MDTextFieldHelperText(text = "For wallmounted products this would be the projection."),
                            form_id = "measurement"
                        ),
                        DropdownInput(
                            data = [
                                {"value": "inches", "text": "in"},
                                {"value": "feet", "text": "ft"},
                                {"value": "milimeters", "text": "mm"},
                                {"value": "centimeters", "text": "cm"}
                            ],
                            form_id = "unit"
                        ),
                        form_id = "depth",
                        adaptive_height = True
                    ),
                    Form(
                        NumberInput(
                            MDTextFieldHintText(text = "Variation Weight"),
                            form_id = "measurement"
                        ),
                        DropdownInput(
                            data = [
                                {"value": "pounds", "text": "lb"},
                                {"value": "kilograms", "text": "kg"}
                            ],
                            form_id = "unit"
                        ),
                        form_id = "weight",
                        adaptive_height = True
                    ),
                    form_id = "specifications",
                    orientation = "vertical",
                    adaptive_height = True
                ),
                MDLabel(text = "UL Info", adaptive_size = True),
                CheckGroup(
                    CheckboxInput(label = "Dry Environments", value = "Dry", group = f"UL_{self.default_name}", adaptive_height = True),
                    CheckboxInput(label = "Damp Environments", value = "Damp", group = f"UL_{self.default_name}", adaptive_height = True),
                    CheckboxInput(label = "Wet Environments", value = "Wet", group = f"UL_{self.default_name}",  adaptive_height = True),
                    CheckboxInput(label = "None", group = f"UL_{self.default_name}", active = True,  adaptive_height = True),
                    form_id = "ul",
                    adaptive_height = True
                ),
                MDLabel(text = "Bulb Info", adaptive_size = True),
                Form(
                    Form(
                        DropdownInput(
                            data = [
                                {"value": "Standard", "text": "Standard"},
                                {"value": "Torpedo", "text": "Torpedo"},
                                {"value": "Candle", "text": "Candle"},
                                {"value": "Diamond", "text": "Diamond"},
                                {"value": "Globe", "text": "Globe"},
                                {"value": "Reflector", "text": "Reflector"},
                                {"value": "Tubular", "text": "Tubular"},
                                {"value": "Vintage", "text": "Vintage"},
                                {"value": "Proprietary", "text": "Proprietary"}
                            ],
                            form_id = "name"
                        ),
                        TextInput(
                            MDTextFieldHintText(text = "Bulb Shape"),
                            MDTextFieldHelperText(text = "The shape colloquial name and code. (Example: Standard (A19))"),
                            form_id = "code"
                        ),
                        form_id = "shape",
                        adaptive_height = True
                    ),
                    Form(
                        DropdownInput(
                            data = [
                                {"value": "Medium", "text": "Medium Base"},
                                {"value": "Candelabra", "text": "Candelabra Base"},
                                {"value": "Pin", "text": "Pin Base"},
                                {"value": "Builtin", "text": "Builtin"}
                            ],
                            form_id = "name"
                        ),
                        TextInput(
                            MDTextFieldHintText(text = "Bulb Socket"),
                            MDTextFieldHelperText(text = "The socket type colloquial name and code. (Example: Medium (E26))"),
                            form_id = "code"
                        ),
                        form_id = "socket",
                        adaptive_height = True
                    ),
                    NumberInput(
                        MDTextFieldHintText(text = "Bulb Quantity"),
                        MDTextFieldHelperText(text = "The amount of bulbs the fixture needs."),
                        form_id = "quantity"
                    ),
                    TextInput(
                        MDTextFieldHintText(text = "Bulb Specifications"),
                        MDTextFieldHelperText(text = "The wattage, lumens, CRI, and life of the bulb."),
                        form_id = "specifications"
                    ),
                    form_id = "bulb",
                    orientation = "vertical",
                    adaptive_height = True
                ),
                MDLabel(text = "Replacements", adaptive_size = True),
                ReplacementForm(),
                TextInput(
                    MDTextFieldHintText(text = "Variation Notes"),
                    MDTextFieldHelperText(text = "Any additional information that needs to be included."),
                    form_id = "notes"
                ),
                TextInput(
                    MDTextFieldHintText(text = "Real UAID"),
                    MDTextFieldHelperText(text = "Some items are variations of other with their own ID."),
                    form_id = "real_id"
                ),
                orientation = "vertical",
                size_hint_x = 0.5,
                adaptive_height = True,
                pos_hint = {"top": 1}
            ),
            orientation = "horizontal",
            adaptive_height = True,
            padding = ['20dp', '30dp'],
        )
        self.add_widget(self.__form)

        self.md_bg_color = self.theme_cls.surfaceBrightColor

    def prefill(self, data):
        overview = data.pop("overview")
        data.update(overview)

        VariationForm.change_variation_number(self.__variation_number + 1)

        self.__form.prefill(data)

    def submit(self):
        form_data = self.__form.submit()[1]

        overview = {}
        for key in ["finishes", "options", "bulb", "replacements", "ul", "specifications", "notes", "real_id"]:
            overview[key] = form_data.pop(key)
        form_data["overview"] = overview

        return "__variation", form_data

    def rename_tab(self, text):
        if hasattr(self, "tab_item"):
            self.tab_item.rename(text)

class ProductForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, on_cancel = None, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.__old_product_id = None
        self.__on_submit = on_submit

        self.variation_number = 1

        variation_forms = TabForm(form_id = "variations", slide = VariationForm)
        self.__form = Form(
            Form(
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Product Name"),
                        MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"Loft Light\""),
                        size_hint_x = 0.6,
                        form_id = "name"
                    ),
                    TextInput(
                        MDTextFieldHintText(text = "Product ID"),
                        MDTextFieldHelperText(text = "Example: for \"UA0040-A\", it would be \"UA0040\""),
                        size_hint_x = 0.4,
                        form_id = "id"
                    ),
                    adaptive_height = True
                ),
                TextInput(
                    MDTextFieldHintText(text = "Product Desctiption"),
                    MDTextFieldHelperText(text = "This is not the product overview"),
                    form_id = "description"
                ),
                orientation = "vertical",
                adaptive_height = True,
                padding = ["20dp", "20dp", "20dp", 0]
            ),
            variation_forms,
            orientation = "vertical",
            adaptive_height = True
        )

        def add_variation_form():
            VariationForm.change_variation_number(self.variation_number)
            variation_forms.add_tab()
            self.variation_number += 1

        def duplicate_variation_form():
            VariationForm.change_variation_number(self.variation_number)
            variation_forms.duplicate_tab()
            self.variation_number += 1

        def remove_variation_form():
            if variation_forms.remove_tab():
                self.variation_number -= 1
                VariationForm.change_variation_number(self.variation_number)

        add_tab = MDIconButton(
            icon = "pencil-plus",
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        add_tab.bind(on_press = lambda *args: add_variation_form())
        duplicate_tab = MDIconButton(
            icon = "content-duplicate",
            style = "standard",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        duplicate_tab.bind(on_press = lambda *args: duplicate_variation_form())
        remove_tab = MDIconButton(
            icon = "trash-can",
            style = "outlined",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        remove_tab.bind(on_press = lambda *args: remove_variation_form())
        submit = MDIconButton(
            icon = "content-save",
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
            MDLabel(text = "Product Information", font_style = "Display", role = "small", adaptive_size = True),
            adaptive_height = True,
            spacing = "20dp",
            padding = ['20dp']
        ))
        self.add_widget(self.__form)
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                add_tab,
                remove_tab,
                duplicate_tab,
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
        self.__old_product_id = None
        self.variation_number = 1

    def default(self):
        self.__reset()
        self.__form.default()

    def prefill(self, id):
        self.__reset()
        self.__old_product_id = id
        self.__form.prefill(Database.get_product(self.__old_product_id))

        self.variation_number = VariationForm.get_variation_number()

    def submit(self):
        if self.__old_product_id:
            Database.update_product(self.__old_product_id, self.__form.submit()[1])
        else:
            Database.create_product(self.__form.submit()[1])
        self.__old_product_id = None
        if self.__on_submit:
            self.__on_submit()
