from kivymd.uix.screen import MDScreen as Screen
from kivymd.uix.label import MDLabel as Label

class Home(Screen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.name = "home"
        
        self.add_widget(Label(text = "Hello World", halign = "center"))
