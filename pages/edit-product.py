from kivymd.uix.screen import MDScreen as Screen
from kivymd.uix.label import MDLabel as Label

class EditProduct(Screen):
    def __init__(self, **kwargs):
        super(EditProduct, self).__init__(**kwargs)
        self.name = "edit-product"
        
        self.add_widget(Label(text = "Goodbye World", halign = "center"))