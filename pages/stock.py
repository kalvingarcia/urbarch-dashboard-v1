from kivymd.uix.screen import MDScreen
from widgets.forms.stockform import StockForm

class Stock(MDScreen):
    def __init__(self, **kwargs):
        super(Stock, self).__init__(**kwargs)
        self.name = "stock"

        self.__stock_id = None
        self.__stock_form = StockForm(on_submit = lambda: self._switch("home"), on_cancel = lambda: self._switch("home"))
        self.add_widget(self.__stock_form)

    def set_id(self, id):
        self.__stock_id = id

    def on_pre_enter(self):
        if self.__stock_id:
            self.__stock_form.prefill(self.__stock_id)
            self.__stock_id = None
        else:
            self.__stock_form.default()