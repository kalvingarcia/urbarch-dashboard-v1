from kivymd.uix.screen import MDScreen
from api.urbandb import UrbanDB
from widgets.datawindow import DataWindow

class AllProducts(MDScreen):
    def __init__(self, **kwargs):
        super(AllProducts, self).__init__(**kwargs)
        self.name = "all-products"

        self.data_window = DataWindow()
        self.add_widget(self.data_window)

    def on_pre_enter(self):
        self.data_window.update(UrbanDB.get_product_list(), lambda uaid: self.edit_screen(uaid))

    def edit_screen(self, uaid):
        edit_screen = self.manager.get_screen("edit-product")
        edit_screen.populate_page(uaid)
        self.manager.current = "edit-product"

