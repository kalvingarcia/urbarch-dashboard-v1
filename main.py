from kivy.core.window import Window
from kivymd.app import MDApp as App

from api.screenmaker import ScreenMaker
from api.urbandb import UrbanDB

class UrbanDashApp(App):
    def __init__(self, **kwargs):
        super(UrbanDashApp, self).__init__(**kwargs)

        # initializing the database connection
        UrbanDB.open_pygres("./sessions/database-env.json")
        UrbanDB.initialize_database()

        # theming the dash
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        # binding the close function
        Window.bind(on_request_close = self.on_request_close)
        Window.size = (1600, 900)

    def build(self):
        self.title = "Urban Dash"
        return ScreenMaker()

    def on_request_close(self, *args):
        UrbanDB.close_pygres()
        self.stop()

if __name__ == "__main__":
    UrbanDashApp().run()