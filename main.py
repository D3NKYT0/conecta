import os
import config

from kivymd.app import MDApp

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager

# banco de dados (mongodb)
from resources.database import Database

# app pra dev
from debug import LiveApp
from dev.icon_search import IconApp

# screens
from screens.start import StartScreen  # <-- primeira tela
from screens.login import LoginScreen  # <-- tela de auth
from screens.index import IndexScreen  # <-- app inicial
from screens.api import ApiScreen  # <-- tela de teste

# controle de desenvolvimento
IS_LIVE = False  # se TRUE liga o app de live caso contrario app normal
IS_ICON = False  # se TRUE liga o app de icons caso contrario app normal


class AgeApp(MDApp):

    Window.size = (1280, 720)

    def __init__(self, token, host, data, **kwargs):
        super().__init__(**kwargs)
        self.__version__ = "0.0.11.10"
        self.token = token
        self.manager = ScreenManager()
        self.DEBUG = False
        self.RAISE_ERROR = False
        self.data = data

        self.db: Database = Database(self)
        self.apihost = host

        self.username = StringProperty(None)
        self.password = StringProperty(None)

    def build(self):

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"

        Builder.load_file("kvs/start.kv")
        self.manager.add_widget(StartScreen(name="start"))

        Builder.load_file("kvs/login.kv")
        self.manager.add_widget(LoginScreen(self, name="login"))

        Builder.load_file("kvs/index.kv")
        self.manager.add_widget(IndexScreen(self, name="index"))

        Builder.load_file("kvs/api.kv")
        self.manager.add_widget(ApiScreen(self, name="api"))

        return self.manager

    def get_application_config(self) -> object:
        if not self.username:
            return super(AgeApp, self).get_application_config()
        conf_directory = self.user_data_dir + '/' + self.username
        if not os.path.exists(conf_directory):
            os.makedirs(conf_directory)
        return super(AgeApp, self).get_application_config('%s/config.cfg' % conf_directory)


if __name__ == '__main__':

    if IS_LIVE:
        data_debug = {
            "CLASSES": {
                "MainScreenManager": "dev.manager.screenmanager",
                "ScreenNow": "dev.manager.screennow",
            },
            "KV_FILES": {
                os.path.join(os.getcwd(), "dev/manager/screenmanager.kv"),
                os.path.join(os.getcwd(), "dev/manager/screennow.kv"),
            }
        }
        LiveApp(data_callback=data_debug, data=config.data).run()

    elif IS_ICON:
        IconApp().run()
        
    else:
        AgeApp(token=config.data["token"], host=config.APIHOST, data=config.data).run()
