from kivy.app import App
from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.datatables.datatables import CellRow
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.color_definitions import colors

from resources import widgets, utils
from random import choice, randint
from copy import deepcopy


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
        self.rd_tb = list()
        self.rd_rp = list()

    def on_check_press_tb(self, table: MDDataTable, row: list, *args):

        if row in self.rd_tb:
            self.rd_tb.remove(row)
        else:
            self.rd_tb.append(row)

    def on_row_press_tb(self, instance_table: MDDataTable, instance_row: CellRow, *args):
        pass

    def on_check_press_rp(self, table: MDDataTable, row: list, *args):

        if row in self.rd_rp:
            self.rd_rp.remove(row)
        else:
            self.rd_rp.append(row)

    def on_row_press_rp(self, instance_table: MDDataTable, instance_row: CellRow, *args):
        pass

    def restart_data_table_tb(self):
        if self.table is not None:
            self.ids.data_box.remove_widget(self.table)
        self.table = MDDataTable(
            use_pagination=True,
            check=True,
            rows_num=10,
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
        self.table.bind(on_check_press=self.on_check_press_tb)
        self.table.bind(on_row_press=self.on_row_press_tb)
        self.ids.data_box.add_widget(self.table)
        self.rd_tb = list()

    def restart_data_table_rp(self):
        self.ids.data_response.remove_widget(self.tb_response)
        self.tb_response = MDDataTable(
            use_pagination=True,
            check=True,
            rows_num=10,
            column_data=[
                ("ID", dp(20)),
                ("Status", dp(30)),
                ("Nome", dp(50)),
                ("CPF", dp(30))
            ]
        )
        self.tb_response.bind(on_check_press=self.on_check_press_rp)
        self.tb_response.bind(on_row_press=self.on_row_press_rp)
        self.ids.data_response.add_widget(self.tb_response)
        self.rd_tb = list()

    def on_pre_leave(self, *args):

        self.restart_data_table_rp()
        self.restart_data_table_tb()

        return super().on_pre_leave(*args)

    def on_pre_enter(self, *args):

        self.token = App.get_running_app().token
        self.user = App.get_running_app().USER_LOGGED

        self.ids.data.text = str(self.clock.date)
        self.ids.hora.text = str(self.clock.hour)

        self.ids.machine.text = str(self.hardware['hostname']).upper()
        self.ids.user.text = str(App.get_running_app().username).upper()

        self.ids.user_name.text = str(self.user['name']).upper()
        self.ids.ip_address.text = str(self.hardware['ip-address'])

        self.updateButton()
        self.restart_data_table_rp()

        App.get_running_app().animate(self.ids.information)

        return super().on_pre_enter(*args)

    def updateButton(self):
        self.restart_data_table_tb()

        # --------------------------------
        # pegar dados do banco
        # --------------------------------

        dados_do_banco = randint(5, 10)  # simulação de solicitação dos dados do banco
        db_data = [n for n in range(dados_do_banco)]  # criação da lista de retorno de dados para iteração

        _id = 1
        for _ in db_data:
            row_now = deepcopy(choice(self.row_data_all))
            row_now.insert(0, f"{_id}")
            _id += 1
            self.add_row_data_table(row_now)

    def consultaButton(self):
        rows_checks = self.rd_tb

        if len(rows_checks) < 1:
            return self.get_message("Você nao selecionou nenhuma solicitação!", colors['Yellow']['500'])

        for row in rows_checks:
            if row[1].lower() == "responder":
                return self.get_message("Você já consultou essa solicitação!", colors['Yellow']['500'])

        # --------------------------------
        # fazer solicitação de API aqui
        # gravar dados no banco
        # atualizar registros da solicitação
        # --------------------------------

        _id = 1
        for _ in rows_checks:
            row_now = deepcopy(choice(self.row_response_all))
            row_now.insert(0, f"{_id}")
            _id += 1
            self.add_row_data_response(row_now)

        self.updateButton()

        self.get_message("Consulta feita com sucesso!", colors['Green']['500'], "#ffffff")

    def reponseButton(self):
        rows_checks = self.rd_tb
        
        if len(rows_checks) < 1:
            return self.get_message("Você nao selecionou nenhuma solicitação!", colors['Yellow']['500'])

        for row in rows_checks:
            if row[1].lower() == "consultar":
                return self.get_message("Você nao pode responder uma solicitação que nao foi consultada!", colors['Yellow']['500'])

        # --------------------------------
        # atualizar as solicitações no banco
        # --------------------------------

        self.updateButton()

        self.get_message("Resposta feita com sucesso!", colors['Green']['500'], "#ffffff")

    def downloadButton(self):
        rows_checks = self.rd_rp

        if len(rows_checks) < 1:
            return self.get_message("Você nao selecionou nenhuma solicitação!", colors['Yellow']['500'])

        self.restart_data_table_rp()

        self.get_message("Arquivos baixados com sucesso!", colors['Green']['500'], "#ffffff")

    def add_row_data_table(self, row, *args):
        self.table.row_data.insert(0, row)

    def add_row_data_response(self, row, *args):
        self.tb_response.row_data.insert(0, row)

    def get_message(self, text: str, color, text_color="#000000"):
        self.bar = MDSnackbar(MDLabel(text=text, theme_text_color="Custom", text_color=text_color), md_bg_color=color)
        self.bar.open()

    def backScreen(self, *args):
        App.get_running_app().manager.current = 'index'
        App.get_running_app().manager.get_screen('index')
