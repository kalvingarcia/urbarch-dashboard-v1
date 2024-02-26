from kivymd.uix.screen import MDScreen as Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from api.urbandb import UrbanDB
from widgets.forms.form import Form
from widgets.forms.productform import ProductForm
from widgets.forms.variationform import VariationForm
from api.makr import screen_unit

class CreateProduct(Screen):
    def __init__(self, **kwargs):
        super(CreateProduct, self).__init__(**kwargs)
        self.name = "create-product"

        variation_form = VariationForm()
        self.creation_form = Form(
                ProductForm(),
                variation_form,
                orientation = "vertical",
        )

        add_tab_button = MDButton(
            MDButtonText(text = "Add Variation"),
            style = "tonal",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        add_tab_button.bind(on_press = lambda *args: variation_form.add_tab())
        remove_tab_button = MDButton(
            MDButtonText(text = "Remove Variation"),
            style = "outlined",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        remove_tab_button.bind(on_press = lambda *args: variation_form.remove_tab())
        submit_button = MDButton(
            MDButtonText(text = "Create Product"),
            style = "filled",
            pos_hint = {"center_x": 0.5, "center_y": 0.5},
        )
        submit_button.bind(on_press = self._send_product)

        self.add_widget(MDBoxLayout(
            self.creation_form,
            MDBoxLayout(
                MDBoxLayout(
                    add_tab_button,
                    remove_tab_button,
                    adaptive_height = True,
                    size_hint_x = 0.5
                ),
                submit_button,
                padding = ['20dp'],
                adaptive_height = True,
            ),
            orientation = "vertical",
            adaptive_height = True,
        ))

    def _send_product(self, *args):
        UrbanDB.create_product(self.creation_form.submit()[1])
        self.manager.current = "all-products"

