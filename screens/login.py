from kivymd.uix.screen import MDScreen
from kivymd.color_definitions import colors
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex as hex
from kivy.properties import StringProperty
from kivy.lang import Builder

import requests
import json

from resources import utils, encrypter

import sys
sys.path.insert(1, './config')

import config

from auth.utils_hash import Core


core = Core()
FOR_TEST = False  # Default: False


class ContentEmail(BoxLayout):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


KV = '''
<ContentEmail>:
    orientation: "vertical"
    size_hint_y: None
    height: "250dp"

    MDTextField:
        id: email_field_verify
        hint_text: "Email"
        icon_right: 'email'
        validator: "email"
        icon_right_color: app.theme_cls.primary_color
        write_tab: False

    MDTextField:
        id: code_field_verify
        hint_text: "Codigo de Verificação"
        icon_right: 'script-text-key'
        required: True
        icon_right_color: app.theme_cls.primary_color
        write_tab: False

    ClickableTextFieldRound:
        id: password_field_verify
        hint_text: "Nova Senha"

    ClickableTextFieldRound:
        id: confirm_password_field_verify
        hint_text: "Confirmar Nova Senha"
'''
Builder.load_string(KV)


class LoginScreen(MDScreen):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.host = self.app.apihost
        self.token = self.app.token
        self.bar = None
        self.dialog = None
        self.is_decripted = False
        self.is_logged = False
        self.is_token_valid = True

    def on_pre_leave(self, *args):
        self.is_decripted = False
        return super().on_pre_leave(*args)

    def on_pre_enter(self, *args):

        self.host = App.get_running_app().apihost

        if self.token['is_active']:
            if not self.is_decripted:
                self.get_token_mongo(self.token["user_id"])
                self.is_decripted = True
            self.ids.login_field.text = self.token["login"]
            self.ids.password_field.text = self.token["password"]
        else:
            self.ids.login_field.text = ""
            self.ids.password_field.text = ""
        return super().on_pre_enter(*args)

    def db_is_active(self, login):
        try:
            collection = "users" if App.get_running_app().environment == "Produção" else "homo_users"
            cl_users = self.app.db.cd(collection)
            user = cl_users.find_one({"_id": self.token['user_id']})
            bearer = encrypter.decrypt_text(self.token['Bearer'], user['data']['bearer']['iv'], user['data']['bearer']['key'])
            headers = {"Authorization": f"Bearer {bearer}"}
            hash, key_hash = core.do_hash()
            headers['conecta-age-hash'] = hash
            headers['conecta-age-key'] = key_hash
            response = requests.get(f"{self.host}/ti/search/user/{login}", headers=headers, timeout=10.0)

            if int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return False

            if int(response.status_code) == 401:
                self.get_message("Token Invalido ou Expirado, tente novamente!", colors['Yellow']['500'])
                self.is_token_valid = False
                return False

            try:
                App.get_running_app().user_now_data = json.loads(response.content)
            except json.decoder.JSONDecodeError:
                self.get_message("Erro no servidor da API, contate o setor de TI!", colors['Red']['500'], "#ffffff")
                return False

            classifier_as = App.get_running_app().user_now_data['classified_as']
            if int(classifier_as) not in [2, 4, 5, 8]:
                self.get_message("Sua conta nao tem acesso a esse aplicativo, verifique com o TI!", colors['Yellow']['500'])
                return False
            
            if int(classifier_as) not in [2] and App.get_running_app().environment != "Produção":
                self.get_message("Sua conta não tem acesso ao servidor de homologação, mude para PRODUÇÃO!", colors['Yellow']['500'])
                return False
            
            return True

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return False

    def get_token_mongo(self, user_id):

        collection = "users" if App.get_running_app().environment == "Produção" else "homo_users"
        cl_users = self.app.db.cd(collection)
        user = cl_users.find_one({"_id": user_id})
        
        if user is None:
            self.token = {"Bearer": "", "is_active": False, "login": "", "password": "", "user_id": ""}
            return 

        try:
            login = encrypter.decrypt_text(self.token['login'], user['data']['login']['iv'], user['data']['login']['key'])
            password = encrypter.decrypt_text(self.token['password'], user['data']['password']['iv'], user['data']['password']['key'])
            bearer = encrypter.decrypt_text(self.token['Bearer'], user['data']['bearer']['iv'], user['data']['bearer']['key'])
            self.token = {"Bearer": bearer, "is_active": True, "login": login, "password": password, "user_id": user_id}

        except ValueError:
            self.token = {"Bearer": "", "is_active": False, "login": "", "password": "", "user_id": ""}
            return 

    def enter(self, email, password):
        if len(email) > 0 and len(password) > 0:
            self.do_login(email, password)
        else:
            self.get_message("Você precisa digitar o email e a senha!", colors['Yellow']['500'])

    def get_token(self, login, password):

        collection = "tokens" if App.get_running_app().environment == "Produção" else "homo_tokens"
        cl_tokens = self.app.db.cd(collection)
        token_data = cl_tokens.find_one({"_id": login})
        self.is_logged = token_data
        if token_data is None:

            body = json.dumps({"login": login, "password": password})
            headers = {"Content-Type": "application/json"}

            hash, key_hash = core.do_hash()
            headers['conecta-age-hash'] = hash
            headers['conecta-age-key'] = key_hash

            try:
                response = requests.post(f"{self.host}/auth/token", data=body, headers=headers, timeout=10.0)
                content = json.loads(response.content)

            except requests.exceptions.Timeout:
                self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
                return False, dict()

            except json.decoder.JSONDecodeError:
                self.get_message("Erro no servidor da API, contate o setor de TI!", colors['Red']['500'], "#ffffff")
                return False, dict()

            except requests.exceptions.ConnectionError:
                self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
                return False, dict()

            if int(response.status_code) == 200:
                data = {"_id": login, "content": content, "is_logged": True}
                cl_tokens.insert_one(data)

                data['is_logged'] = False  # evitando a validação antes da passagem de tela
                self.is_logged = data

                return True, content

            elif int(response.status_code) == 400:
                self.get_message("Login/Senha Invalidos!", colors['Yellow']['500'])
                return False, content

            elif int(response.status_code) == 403:
                self.get_message("Aplicativo Incompativel!", colors['Purple']['500'], "#ffffff") 
                return False, content

            else:
                self.get_message("Erro desconhecido!", colors['Red']['500'], "#ffffff")
                return False, content

        elif token_data['is_logged']:

            if FOR_TEST:
                self.is_logged['is_logged'] = False
                return True, token_data['content']
            
            if App.get_running_app().environment == "Produção":
                self.get_message("Você já esta logado em outro terminal!", colors['Red']['500'], "#ffffff")
                return False, token_data['content']
            
            else:
                self.is_logged['is_logged'] = False
                return True, token_data['content']

        else:
            cl_tokens.update_one({"_id": login}, {"$set": {"is_logged": True}})
            return True, token_data['content']

    def update_token(self, login, password, bearer, user_id):
        self.token["login"] = login
        self.token["password"] = password
        self.token["Bearer"] = bearer
        self.token["is_active"] = True
        self.token["user_id"] = user_id
        config.update_token(self.token)
        
    def do_login(self, loginText, passwordText):

        response = self.get_token(loginText, passwordText)
        
        if response[0] is True:

            collection = "users" if App.get_running_app().environment == "Produção" else "homo_users"
            cl_users = self.app.db.cd(collection)
            user = cl_users.find_one({"_id": str(response[1]['user']['id'])})
            if user is None:

                login, l_iv, l_key = encrypter.encrypt_text(loginText)
                password, p_iv, p_key = encrypter.encrypt_text(passwordText)
                bearer, b_iv, b_key = encrypter.encrypt_text(response[1]['access_token'])
                user_id = str(response[1]['user']['id'])

                data = {
                    "_id": user_id,
                    "data": {
                        "login": {
                            "text": login, "iv": l_iv, "key": l_key
                        },
                        "password": {
                            "text": password, "iv": p_iv, "key": p_key
                        },
                        "bearer": {
                            "text": bearer, "iv": b_iv, "key": b_key
                        }
                    }
                }

                cl_users.insert_one(data)
                self.update_token(login, password, bearer, user_id)

            else:

                if self.is_logged['is_logged']:
                    return

                self.update_token(user['data']['login']['text'], user['data']['password']['text'], user['data']['bearer']['text'], user['_id'])

            # verificando a disponibilidade do banco de operaçao (postgresql)
            if not self.db_is_active(loginText):
                collection = "tokens" if App.get_running_app().environment == "Produção" else "homo_tokens"
                cl_tokens = self.app.db.cd(collection)
                cl_tokens.update_one({"_id": loginText}, {"$set": {"is_logged": False}})

                if not self.is_token_valid:
                    user_id = str(response[1]['user']['id'])
                    collection = "users" if App.get_running_app().environment == "Produção" else "homo_users"
                    cl_users = self.app.db.cd(collection)
                    cl_tokens.delete_one({"_id": loginText})
                    cl_users.delete_one({"_id": user_id})
                    self.is_token_valid = True
                return

            self.app.username = loginText
            self.app.password = passwordText

            #leva o token para o aplicativo
            self.app.token = self.token
            self.app.USER_LOGGED = response[1]['user']
            self.is_logged['is_logged'] = True

            self.manager.current = 'index'
            self.manager.get_screen('index')

            self.app.config.read(self.app.get_application_config())
            self.app.config.write()

    def backScreen(self):
        App.get_running_app().manager.current = 'start'
        App.get_running_app().manager.get_screen('start')

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def close_dialog(self, *args):
        self.dialog.buttons[1].disabled = False
        self.dialog.dismiss()

    def send_email(self, *args):

        if len(self.dialog.content_cls.ids.email_field_verify.text) < 1:
            return self.get_message("Você precisa digitar um email valido!", colors['Yellow']['500'])

        if "@" not in self.dialog.content_cls.ids.email_field_verify.text:
            return self.get_message("Você precisa digitar um email valido!", colors['Yellow']['500'])

        if "." not in self.dialog.content_cls.ids.email_field_verify.text:
            return self.get_message("Você precisa digitar um email valido!", colors['Yellow']['500'])

        email_text = self.dialog.content_cls.ids.email_field_verify.text
        headers = {"Authorization": f"Bearer {App.get_running_app().system_token}"}
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash

        try:
            response = requests.get(f"{self.host}/ti/search/email/{email_text}", headers=headers, timeout=10.0)
            content = json.loads(response.content)

        except requests.exceptions.Timeout:
            self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        except requests.exceptions.ConnectionError:
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        except json.decoder.JSONDecodeError:
            self.get_message("Erro no servidor da API, contate o setor de TI!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        if int(response.status_code) == 401:
            return self.get_message("Você nao tem autorização para fazer isso!", colors['Red']['500'], "#ffffff")

        if int(response.status_code) == 500:
            self.get_message("Erro no servidor!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        if int(response.status_code) != 200:
            return self.get_message("Você precisa digitar um email cadastrado!", colors['Yellow']['500'])

        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash
        self.validation_code = utils.create_code()
        self.user_recovery = content
        body = json.dumps({"destination_email": email_text, "subject": "Codigo de Verificação", "content": self.validation_code})

        try:
            response = requests.post(f"{self.host}/ti/send/email", data=body, headers=headers, timeout=10.0)

        except requests.exceptions.Timeout:
            self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        except requests.exceptions.ConnectionError:
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            return self.close_dialog()

        if int(response.status_code) == 401:
            self.get_message("Você nao tem autorização para fazer isso!", colors['Red']['500'], "#ffffff")

        if int(response.status_code) == 500:
            self.get_message("Erro no servidor!", colors['Red']['500'], "#ffffff")
            self.close_dialog()

        if int(response.status_code) == 202:
            self.get_message("Email enviado com sucesso!", colors['Green']['500'], "#ffffff")
            self.dialog.buttons[1].disabled = True

    def change_password(self, *args):

        email = self.dialog.content_cls.ids.email_field_verify.text
        code = self.dialog.content_cls.ids.code_field_verify.text
        password = self.dialog.content_cls.ids.password_field_verify.ids.text_field.text
        confirm = self.dialog.content_cls.ids.confirm_password_field_verify.ids.text_field.text

        if len(email) == 0:
            return self.get_message("Você precisa digitar um email!", colors['Yellow']['500'])

        if "@" not in email and "." not in email:
            return self.get_message("Você precisa digitar um email valido!", colors['Yellow']['500'])

        if len(code) < 1:
            return self.get_message("Você precisa digitar um codigo!", colors['Yellow']['500'])

        if len(password) < 1:
            return self.get_message("Você precisa digitar uma senha!", colors['Yellow']['500'])

        if len(confirm) < 1:
            return self.get_message("Você precisa confirmar sua senha!", colors['Yellow']['500'])

        try:
            if self.validation_code != code:
                return self.get_message("Codigo de verificação incorreto!", colors['Yellow']['500'])
        except AttributeError:
            return self.get_message("Você precisa clicar no botao [ENVIAR CODIGO] antes de confirmar!", colors['Yellow']['500'])

        if password != confirm:
            return self.get_message("As senhas nao conferem!", colors['Yellow']['500'])

        headers = {"Content-Type": "application/json"}
        headers["Authorization"] = f"Bearer {App.get_running_app().system_token}"
        hash, key_hash = core.do_hash()
        headers['conecta-age-hash'] = hash
        headers['conecta-age-key'] = key_hash
        body = json.dumps({"password": password})

        try:
            user_id = self.user_recovery['id']
            response = requests.put(f"{self.host}/ti/change/password/{user_id}", data=body, headers=headers, timeout=10.0)

        except requests.exceptions.Timeout:
            self.get_message("Falha na comunicação!", colors['Red']['500'], "#ffffff")
            self.close_dialog()

        except requests.exceptions.ConnectionError:
            self.get_message("Servidor fora de serviço!", colors['Red']['500'], "#ffffff")
            self.close_dialog()

        if int(response.status_code) == 401:
            self.get_message("Você nao tem autorização para fazer isso!", colors['Red']['500'], "#ffffff")

        if int(response.status_code) == 500:
            self.get_message("Erro no servidor!", colors['Red']['500'], "#ffffff")
            self.close_dialog()

        if int(response.status_code) == 200:
            self.get_message("Senha alterada com sucesso!", colors['Green']['500'], "#ffffff")
            self.dialog.buttons[1].disabled = False
            self.close_dialog()

    def show_popup(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Digite seu email abaixo:",
                type="custom",
                content_cls=ContentEmail(),
                buttons=[
                    MDFlatButton(
                        text="CANCELA",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="red",
                        on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text="ENVIAR CODIGO",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="green",
                        on_release=self.send_email
                    ),
                    MDFlatButton(
                        text="CONFIRMA",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color=hex('#153788'),
                        on_release=self.change_password
                    )
                ],
            )
        self.dialog.content_cls.ids.email_field_verify.text = ""
        self.dialog.content_cls.ids.code_field_verify.text = ""
        self.dialog.content_cls.ids.password_field_verify.text = ""
        self.dialog.content_cls.ids.confirm_password_field_verify.text = ""
        self.dialog.buttons[1].disabled = False
        self.dialog.open()
