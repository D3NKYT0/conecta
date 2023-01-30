import os
import config

from kivymd.app import MDApp

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# banco de dados (mongodb)
from resources.database import Database

# app pra dev
from debug import LiveApp
from dev.icon_search import IconApp

# screens
from screens.start import StartScreen  # <-- primeira tela
from screens.login import LoginScreen  # <-- tela de auth
from screens.index import IndexScreen  # <-- app inicial
from screens.spc import SpcScreen  # <-- tela do spc
from screens.api import ApiScreen  # <-- tela de teste

# controle de desenvolvimento
IS_LIVE = False  # se TRUE liga o app de live caso contrario app normal
IS_ICON = False  # se TRUE liga o app de icons caso contrario app normal


class AgeApp(MDApp):

    Window.size = (1280, 720)
    title = 'Conecta Age'
    icon = 'images/icons/app.png'

    def __init__(self, config_app, **kwargs):
        super().__init__(**kwargs)
        self.__version__ = "0.0.15.1"
        self.config_app = config_app
        self.token = self.config_app.data["token"]
        self.apihost = self.config_app.APIHOST
        
        self.DEBUG = False
        self.RAISE_ERROR = False
        self.EXIT_POPUP = None
        self.USER_LOGGED = None

        self.manager = ScreenManager()
        self.db: Database = Database(self)
        
        self.username = StringProperty(None)
        self.password = StringProperty(None)

    def build(self):

        Window.bind(on_request_close=self.exit_app_x)
        Window.bind(on_keyboard=self.exit_app_esc)

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

        Builder.load_file("kvs/spc.kv")
        self.manager.add_widget(SpcScreen(self, name="spc"))

        return self.manager

    def exit_app_esc(self, window, key, *args):
        if key == 27:
            self.on_popup_close()
            return True

    def exit_app_x(self, *args):
        self.on_popup_close()
        return True

    def on_popup_close(self, *args):
        if not self.EXIT_POPUP:
            self.EXIT_POPUP = MDDialog(
                title='Sair do ConectaAge',
                text="Deseja mesmo sair?",
                buttons=[
                    MDFlatButton(
                        text="CANCELA",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="red",
                        on_press=lambda x: self.close_exit_dialog()
                    ),
                    MDFlatButton(
                        text="CONFIRMA",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color='#153788',
                        on_press=lambda x: self.close_app_confirm()
                    )
                ],
            )
        self.EXIT_POPUP.open()

    def close_app_confirm(self, *largs):
        if self.USER_LOGGED:
            cl_tokens = self.db.cd("tokens")
            cl_users = self.db.cd("users")
            cl_tokens.delete_one({"_id": self.username})
            cl_users.delete_one({"_id": self.USER_LOGGED["id"]})
        super(AgeApp, self).stop(*largs)

    def close_exit_dialog(self, *args):
        self.EXIT_POPUP.dismiss()

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
        AgeApp(config_app=config).run()
