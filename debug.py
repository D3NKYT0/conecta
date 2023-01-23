from kaki.app import App
from kivymd.app import MDApp
from kivy.factory import Factory
from kivy.core.window import Window


class LiveApp(MDApp, App):

    DEBUG = 1
    KV_FILES = dict()
    CLASSES = dict()
    AUTORELOADER_PATHS = [(".", {"recursive": True}),]
    Window.size = (1280, 720)

    def __init__(self, data_callback, data, **kwargs):
        super().__init__(**kwargs)
        self.data_callback = data_callback
        self.data = data
        self.CLASSES = self.data_callback["CLASSES"]
        self.KV_FILES = self.data_callback['KV_FILES']

    def build_app(self):

        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"

        return Factory.MainScreenManager()


if __name__ == "__main__":
    LiveApp().run()
