from kivymd.uix.screen import MDScreen
from widgets.forms.productform import ProductForm

class Product(MDScreen):
    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        self.name = "product"

        self.__product_id = None
        self.__product_form = ProductForm(on_submit = lambda: self._switch("home"), on_cancel = lambda: self._switch("home"))
        self.add_widget(self.__product_form)

    def set_id(self, id):
        self.__product_id = id

    def on_pre_enter(self):
        if self.__product_id:
            self.__product_form.prefill(self.__product_id)
            self.__product_id = None
        else:
            self.__product_form.default()

