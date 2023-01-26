from kivymd.uix.screen import MDScreen

from kivy.app import App

from kivymd.uix.datatables import MDDataTable
from random import choice
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.color_definitions import colors

from resources import widgets, utils

from kivy.metrics import dp


class SpcScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None
        self.tb_response = None
        self.token = None
        self.clock = widgets.ClockRealTime(widget=self).start()
        self.hardware = utils.getSystemInfo()
        self.row_response_all = App.get_running_app().config_app.row_response_all
        self.row_data_all = App.get_running_app().config_app.row_data_all

    def on_pre_enter(self, *args):

        self.token = App.get_running_app().token
        self.user = App.get_running_app().USER_LOGGED

        self.ids.data.text = str(self.clock.date)
        self.ids.hora.text = str(self.clock.hour)

        self.ids.machine.text = str(self.hardware['hostname']).upper()
        self.ids.user.text = str(App.get_running_app().username).upper()

        self.ids.user_name.text = str(self.user['name']).upper()
        self.ids.ip_address.text = str(self.hardware['ip-address'])

        self.table = MDDataTable(
            use_pagination=True,
            check=True,
            column_data=[
                ("ID", dp(20)),
                ("Status", dp(30)),
                ("Nome", dp(50)),
                ("CPF", dp(30)),
                ("Municipio", dp(30)),
                ("Agente", dp(30)),
                ("cadastrado em", dp(30)),
            ]
        )
        self.ids.data_box.add_widget(self.table)

        self.tb_response = MDDataTable(
            use_pagination=True,
            check=True,
            column_data=[
                ("ID", dp(20)),
                ("Status", dp(30)),
                ("Nome", dp(50)),
                ("CPF", dp(30))
            ]
        )
        self.ids.data_response.add_widget(self.tb_response)
        return super().on_pre_enter(*args)

    def updateButton(self):
        self.add_row_data_table()
        self.get_message("Atualização feita com sucesso!", colors['Green']['500'], "#ffffff")

    def consultaButton(self):
        self.table.row_data = list()
        self.add_row_data_response()
        self.get_message("Consulta feita com sucesso!", colors['Green']['500'], "#ffffff")

    def reponseButton(self):
        self.tb_response.row_data = list()
        self.get_message("Resposta feita com sucesso!", colors['Green']['500'], "#ffffff")

    def downloadButton(self):
        self.get_message("Função em desenvolvimento!", colors['Yellow']['500'])

    def add_row_data_table(self, *args):
        if self.table:
            self.table.row_data.insert(0, choice(self.row_data_all))

    def add_row_data_response(self, *args):
        if self.tb_response:
            self.tb_response.row_data.insert(0, choice(self.row_response_all))

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def backScreen(self, *args):
        App.get_running_app().manager.current = 'index'
        App.get_running_app().manager.get_screen('index')
