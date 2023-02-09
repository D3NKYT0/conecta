import json
import requests

from kivymd.uix.screen import MDScreen
from kivymd.color_definitions import colors
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel

from functools import partial
from kivymd.uix.menu import MDDropdownMenu

from kivy.app import App
from auth.utils_hash import Core

from resources import widgets, utils, encrypter


core = Core()


class ApiScreen(MDScreen):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.ep = self.app.config_app.data['endpoints']
        self.bar = None
        self.token = None
        self.clock = widgets.ClockRealTime(widget=self).start()
        self.hardware = utils.getSystemInfo()

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def cb_menu(self, text):
        self.ids.menu_endpoint.text = text
        self.menu_ep.dismiss()

    def on_pre_enter(self, *args):

        self.token = self.app.token
        self.user = self.app.USER_LOGGED

        cl_users = self.app.db.cd("users")
        user = cl_users.find_one({"_id": self.token['user_id']})
        self.bearer = encrypter.decrypt_text(self.token['Bearer'], user['data']['bearer']['iv'], user['data']['bearer']['key'])

        self.ids.data.text = str(self.clock.date)
        self.ids.hora.text = str(self.clock.hour)

        self.ids.machine.text = str(self.hardware['hostname']).upper()
        self.ids.user.text = str(self.app.username).upper()

        self.ids.user_name.text = str(self.user['name']).upper()
        self.ids.ip_address.text = str(self.hardware['ip-address'])
        
        self.menu_items = [{"viewclass": "OneLineListItem",
                            "text": f"{i}",
                            "font_style": "H5",
                            "theme_text_color": "Custom",
                            "text_color": [1, 1, 1, 1],
                            "bg_color": '#153788',
                            "on_release": partial(self.cb_menu, f"{i}")} 
                            for i in self.ep['categories']]

        self.menu_ep = MDDropdownMenu(items=self.menu_items, width_mult=4, caller=self.ids.menu_endpoint)
        self.menu_ep.bind()

        App.get_running_app().animate(self.ids.information)

        return super().on_pre_enter(*args)

    def backScreen(self, *args):
        App.get_running_app().manager.current = 'index'
        App.get_running_app().manager.get_screen('index')

    def buttonGetOne(self):

        if len(self.ids.field_id.text) == 0:
            self.ids.response.text = "O ID É NECESSARIO!"
            return 
        
        if self.ids.menu_endpoint.text == "CHOICE ENDPOINT":
            self.ids.response.text = "VOCE PRECISA ESCOLHER O ENDPOINT"
            return

        url_request = f"{self.ep['host']}" + f"{self.ids.menu_endpoint.text}" + f"get/{self.ids.field_id.text}"
        bearer = self.bearer
        headers = {"Authorization": f"Bearer {bearer}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash

        try:
            response = requests.get(url_request, headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado!", colors['Yellow']['500']) 
                return

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        try:
            parsed = json.loads(response.content)
            json_response = f"{json.dumps(parsed, indent=4)}"
        except json.decoder.JSONDecodeError:
            self.get_message("Erro de JSON no servidor, por favor contatar o setor de TI!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 422:
            self.ids.response.text = json_response

        if int(response.status_code) == 302:
            self.ids.response.text = json_response

        if int(response.status_code) == 404:
            self.ids.response.text = json_response

        if int(response.status_code) == 406:
            self.ids.response.text = json_response

        if int(response.status_code) == 200:
            self.ids.response.text = json_response

    def buttonGetAll(self):
        
        if self.ids.menu_endpoint.text == "CHOICE ENDPOINT":
            self.ids.response.text = "VOCE PRECISA ESCOLHER O ENDPOINT"
            return

        url_request = f"{self.ep['host']}" + f"{self.ids.menu_endpoint.text}" + "get/all/"
        bearer = self.bearer
        headers = {"Authorization": f"Bearer {bearer}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash

        try:
            response = requests.get(url_request, headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado!", colors['Yellow']['500']) 
                return

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        try:
            parsed = json.loads(response.content)
            json_response = f"{json.dumps(parsed, indent=4)}"
        except json.decoder.JSONDecodeError:
            self.get_message("Erro de JSON no servidor, por favor contatar o setor de TI!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 422:
            self.ids.response.text = json_response

        if int(response.status_code) == 302:
            self.ids.response.text = json_response

        if int(response.status_code) == 404:
            self.ids.response.text = json_response

        if int(response.status_code) == 406:
            self.ids.response.text = json_response

        if int(response.status_code) == 200:
            self.ids.response.text = json_response

    def buttonRegister(self):
        
        if self.ids.menu_endpoint.text == "CHOICE ENDPOINT":
            self.ids.response.text = "VOCE PRECISA ESCOLHER O ENDPOINT"
            return

        if len(self.ids.field_body.text) == 0:
            self.ids.response.text = "VOCE PRECISA INSERIR O BODY"
            return

        try:
            json_object = json.loads(self.ids.field_body.text)
        except json.decoder.JSONDecodeError:
            self.ids.response.text = "VOCE PRECISA INSERIR O BODY NO FORMATO DE JSON"
            return

        url_request = f"{self.ep['host']}" + f"{self.ids.menu_endpoint.text}" + "register/"
        bearer = self.bearer
        headers = {"Authorization": f"Bearer {bearer}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash
        body = json.dumps(json_object)

        try:
            response = requests.post(url_request, data=body, headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado!", colors['Yellow']['500']) 
                return

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        try:
            parsed = json.loads(response.content)
            json_response = f"{json.dumps(parsed, indent=4)}"
        except json.decoder.JSONDecodeError:
            self.get_message("Erro de JSON no servidor, por favor contatar o setor de TI!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 422:
            self.ids.response.text = json_response

        if int(response.status_code) == 302:
            self.ids.response.text = json_response

        if int(response.status_code) == 404:
            self.ids.response.text = json_response

        if int(response.status_code) == 406:
            self.ids.response.text = json_response

        if int(response.status_code) == 201:
            self.ids.response.text = json_response

    def buttonUpdate(self):
        
        if len(self.ids.field_id.text) == 0:
            self.ids.response.text = "O ID É NECESSARIO!"
            return 
        
        if self.ids.menu_endpoint.text == "CHOICE ENDPOINT":
            self.ids.response.text = "VOCE PRECISA ESCOLHER O ENDPOINT"
            return

        if len(self.ids.field_body.text) == 0:
            self.ids.response.text = "VOCE PRECISA INSERIR O BODY"
            return

        try:
            dict_object = json.loads(self.ids.field_body.text)
        except json.decoder.JSONDecodeError:
            self.ids.response.text = "VOCE PRECISA INSERIR O BODY NO FORMATO DE JSON"
            return

        url_request = f"{self.ep['host']}" + f"{self.ids.menu_endpoint.text}" + f"update/{self.ids.field_id.text}"
        bearer = self.bearer
        headers = {"Authorization": f"Bearer {bearer}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash
        json_object = json.dumps(dict_object)

        try:    
            response = requests.put(url_request, data=json_object, headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado!", colors['Yellow']['500']) 
                return

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        try:
            parsed = json.loads(response.content)
            json_response = f"{json.dumps(parsed, indent=4)}"
        except json.decoder.JSONDecodeError:
            self.get_message("Erro de JSON no servidor, por favor contatar o setor de TI!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 422:
            self.ids.response.text = json_response

        if int(response.status_code) == 302:
            self.ids.response.text = json_response

        if int(response.status_code) == 404:
            self.ids.response.text = json_response

        if int(response.status_code) == 406:
            self.ids.response.text = json_response

        if int(response.status_code) == 200:
            self.ids.response.text = json_response

    def buttonDelete(self):
        
        if len(self.ids.field_id.text) == 0:
            self.ids.response.text = "O ID É NECESSARIO!"
            return 
        
        if self.ids.menu_endpoint.text == "CHOICE ENDPOINT":
            self.ids.response.text = "VOCE PRECISA ESCOLHER O ENDPOINT"
            return

        url_request = f"{self.ep['host']}" + f"{self.ids.menu_endpoint.text}" + f"delete/{self.ids.field_id.text}"
        bearer = self.bearer
        headers = {"Authorization": f"Bearer {bearer}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash
        
        try:
            response = requests.delete(url_request, headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado!", colors['Yellow']['500']) 
                return

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return

        try:
            parsed = json.loads(response.content)
            json_response = f"{json.dumps(parsed, indent=4)}"
        except json.decoder.JSONDecodeError:
            self.get_message("Erro de JSON no servidor, por favor contatar o setor de TI!", colors['Red']['500'], "#ffffff")
            return

        if int(response.status_code) == 422:
            self.ids.response.text = json_response

        if int(response.status_code) == 302:
            self.ids.response.text = json_response

        if int(response.status_code) == 404:
            self.ids.response.text = json_response

        if int(response.status_code) == 406:
            self.ids.response.text = json_response

        if int(response.status_code) == 200:
            self.ids.response.text = json_response
