from kivymd.uix.textfield import MDTextFieldHelperText, MDTextFieldHintText
from .form import Form, TextInput
from api.makr import screen_unit

class ProductForm(Form):
    def __init__(self, **kwargs):
        super(ProductForm, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.add_widget(Form(
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
            )
        ))
        self.add_widget(TextInput(
            MDTextFieldHintText(text = "Product Desctiption"),
            MDTextFieldHelperText(text = "This is not the product overview"),
            form_id = "description"
        ))

        self.adaptive_height = True