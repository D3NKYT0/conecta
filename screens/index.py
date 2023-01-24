import random

from kivy.app import App
from kivy.utils import get_color_from_hex as hex

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.color_definitions import colors

from resources import encrypter, widgets, utils, data_utils


class IndexScreen(MDScreen):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.token = None
        self.exit_popup = None
        self.is_logged = None
        self.clock = widgets.ClockRealTime(widget=self).start()
        self.hardware = utils.getSystemInfo()

        msg = "Filtros em breve..."
        menu_pre = data_utils.menu_pre_items
        menu_pre[0]['on_release'] = lambda x = msg: self.msg_pre_callback(x)
        menu_consulta = data_utils.menu_pre_items
        menu_consulta[0]['on_release'] = lambda x = msg: self.msg_consulta_callback(x)
        menu_lse = data_utils.menu_pre_items
        menu_lse[0]['on_release'] = lambda x = msg: self.msg_lse_callback(x)
        self.menu_pre = MDDropdownMenu(items=menu_pre, caller=self.ids.button_pre, width_mult=2.5)
        self.menu_consulta = MDDropdownMenu(items=menu_consulta, caller=self.ids.button_consulta, width_mult=2.5)
        self.menu_lse = MDDropdownMenu(items=menu_lse, caller=self.ids.button_lse, width_mult=2.5)

    def msg_pre_callback(self, description):
        self.menu_pre.dismiss()
        self.get_message(description, colors['Yellow']['500'])

    def msg_consulta_callback(self, description):
        self.menu_consulta.dismiss()
        self.get_message(description, colors['Yellow']['500'])

    def msg_lse_callback(self, description):
        self.menu_lse.dismiss()
        self.get_message(description, colors['Yellow']['500'])

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def on_pre_enter(self, *args):

        self.token = self.app.token

        x, y = data_utils.MESES, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        second_data = [data_utils.MESES, [2, 1, 3, 4, 6, 5, 7, 8, 10, 9, 12, 11]]
        title, legends = 'Solititações de Negativação', ['Pedidos de Solicitações', 'Solicitações Efetivadas']
        utils.create_graphics(x, y, second_data, title, legends)

        x_data = [21,22,23,4,5,6,77,8,9,10,31,32,33,34,35,36,37,18,49,50,100]
        utils.create_graphic_bar(x_data)

        data_pie = {
            "labels": ['Ex1', 'Ex2', 'Ex3', 'Ex4'],
            "sizes": [10, 20, 30, 40],
            "explode": [0.05, 0.05, 0.05, 0.05]
                }
        utils.create_graphic_pizza(data_pie)

        self.ids.image_one.reload()
        self.ids.image_two.reload()
        self.ids.image_three.reload()

        self.ids.total_pre.text = utils.format_num(random.randint(1000, 10000))
        self.ids.total_consulta.text = utils.format_num(random.randint(1000, 10000))
        self.ids.total_lse.text = utils.format_num(random.randint(1000, 10000))

        self.user = self.app.USER_LOGGED

        self.ids.data.text = str(self.clock.date)
        self.ids.hora.text = str(self.clock.hour)

        self.ids.machine.text = str(self.hardware['hostname']).upper()
        self.ids.user.text = str(self.app.username).upper()

        self.ids.user_name.text = str(self.user['name']).upper()
        self.ids.ip_address.text = str(self.hardware['ip-address'])
        
        cl_users = self.app.db.cd("users")
        user = cl_users.find_one({"_id": self.token['user_id']})
        login = encrypter.decrypt_text(self.token['login'], user['data']['login']['iv'], user['data']['login']['key'])

        cl_tokens = self.app.db.cd("tokens")
        token_data = cl_tokens.find_one({"_id": login})
        self.is_logged = token_data

        classifier_as = App.get_running_app().user_now_data['classified_as']
        if int(classifier_as) in [2]:
            self.ids.debug.text = "DEGUB"

        return super().on_pre_enter(*args)

    def debug(self):
        App.get_running_app().manager.current = 'api'
        App.get_running_app().manager.get_screen('api')

    def backScreen(self, *args):

        if self.is_logged is not None:
            cl_tokens = self.app.db.cd("tokens")
            token_data = cl_tokens.find_one({"_id": self.is_logged['_id']})
            if token_data is not None:
                cl_tokens.update_one({"_id": self.is_logged['_id']}, {"$set": {"is_logged": False}})
                self.is_logged = None

            App.get_running_app().manager.current = 'login'
            App.get_running_app().manager.get_screen('login')

        self.close_exit_popup()

    def close_exit_popup(self, *args):
        self.exit_popup.dismiss()

    def dialog_spam(self):
        close_button = MDFlatButton(
                        text="Não",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color="red",
                        on_release=self.close_exit_popup
                    )
        delete_button = MDFlatButton(
                        text="Sim",
                        theme_text_color="Custom",
                        text_color="white",
                        md_bg_color=hex('#153788'),
                        on_release=self.backScreen
                    )

        if self.exit_popup is None:
            self.exit_popup = MDDialog(
                title='Fazer Logoff',
                text="Deseja sair realmente?",
                buttons=[close_button, delete_button],
                )

        self.exit_popup.open()
