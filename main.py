from kivymd.app import MDApp as App
from api.screenmaker import ScreenMaker

class UrbanDashApp(App):
    def build(self):
        self.title = "Urban Dash"
        return ScreenMaker().manager

if __name__ == "__main__":
    UrbanDashApp().run()