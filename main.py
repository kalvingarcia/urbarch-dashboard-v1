from kivy.core.window import Window
from kivymd.app import MDApp
from api.appbuilder import AppBuilder
from api.database import Database

class DashApp(MDApp):
    def __init__(self, **kwargs):
        super(DashApp, self).__init__(**kwargs)

        # initializing the database connection
        Database.connect("./sessions/database-env.json")

        # theming dash
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.set_colors()

        # binding the close function
        Window.bind(on_request_close = self.on_request_close)
        Window.size = (1600, 900)
        Window.minimum_width, Window.minimum_height = (1600, 900)

    def build(self):
        self.title = "Urban Dash"
        return AppBuilder()

    def on_request_close(self, *args):
        Database.disconnect()
        self.stop()

if __name__ == "__main__":
    DashApp().run()