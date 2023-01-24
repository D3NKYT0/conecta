from kivymd.uix.screen import MDScreen
from kivy.app import App

import json
import requests

from kivymd.color_definitions import colors
from auth.utils_hash import Core
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel


core = Core()

try:
    import pyi_splash  # essa importação é referente ao PYINSTALLER (nao precisa ser instalada)
except:
    pass


class StartScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system = App.get_running_app().config_app.SYSTEM
        self.host = App.get_running_app().apihost

    def on_pre_enter(self, *args):
        try:
            pyi_splash.close()
        except:
            pass
        return super().on_pre_enter(*args)

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def login(self):

        body = json.dumps({"login": self.system['login'], "password": self.system['password']})
        headers = {"Content-Type": "application/json"}

        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash

        try:
            response = requests.post(f"{self.host}/auth/su", data=body, headers=headers, timeout=10.0)
            content = json.loads(response.content)

        except requests.exceptions.Timeout:
            self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
            return

        except json.decoder.JSONDecodeError:
            self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
            return

        except requests.exceptions.ConnectionError:
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 200:

            App.get_running_app().system_token = content['access_token']

            App.get_running_app().manager.current = 'login'
            App.get_running_app().manager.get_screen('login')
