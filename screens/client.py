from kivy.app import App

from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import ThreeLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivymd.uix.selectioncontrol.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from resources.widgets import *
from functools import partial
from resources import widgets, utils


class Client(ThreeLineAvatarIconListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClientScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        self.fast_search = "Todos"
        self.clock = widgets.ClockRealTime(widget=self).start()
        self.hardware = utils.getSystemInfo()
        self.ep = list()
        super().__init__(*args, **kwargs)

    def on_pre_enter(self, *args):

        self.user = App.get_running_app().USER_LOGGED

        self.ids.data.text = str(self.clock.date)
        self.ids.hora.text = str(self.clock.hour)

        self.ids.machine.text = str(self.hardware['hostname']).upper()
        self.ids.user.text = str(App.get_running_app().username).upper()

        self.ids.user_name.text = str(self.user['name']).upper()
        self.ids.ip_address.text = str(self.hardware['ip-address'])

        App.get_running_app().animate(self.ids.information)

        return super().on_pre_enter(*args)

    def on_checkbox_active(self, checkbox, value):
        if value:
            for child in self.ids.list_clients.children:
                if isinstance(child, Client): 
                    for wid in child.children:
                        for c in wid.children:
                            if isinstance(c, MDCheckbox):
                                c.state='down'
        else:
            for child in self.ids.list_clients.children:
                if isinstance(child, Client): 
                    for wid in child.children:
                        for c in wid.children:
                            if isinstance(c, MDCheckbox):
                                c.state='normal'

    def change_menu(self, menu):
        if menu == "cpf":
            self.ep = [
                "123.456.789-10",
                "112.223.556-98",
                "321.654.464-71"
            ]
        elif menu == "cidade":
            self.ep = [
            "jaboatao",
            "recife",
            "outros"
        ]
        elif menu == "cliente":
            self.ep = [
            "daniel jose do amaral filho",
            "ricardo dos santos neve",
            "ailton renan george da silva"
        ]
        elif menu == "agente":
            self.ep = [
            "vinicius pau brasil",
            "eduardo carvalho",
            "edilberto acacia"
        ]
        self.start_menu(menu)

    def start_menu(self, menu):
        self.menu_items = [{"viewclass": "OneLineListItem", "text": f"{i}", 
                            "font_style": "H5", "theme_text_color": "Custom", "text_color": [1, 1, 1, 1], 
                            "bg_color": '#153788', "on_release": partial(self.cb_menu, f"{i}", menu)} for i in self.ep]

        self.menu_dropDown = MDDropdownMenu(items=self.menu_items, position="bottom", width_mult=4)
        if menu == "cpf":
            self.menu_dropDown.caller = self.ids.cpf
        elif menu == "cidade":
            self.menu_dropDown.caller = self.ids.city
        elif menu == "cliente":
            self.menu_dropDown.caller = self.ids.name
        elif menu == "agente":
            self.menu_dropDown.caller = self.ids.agent
        self.menu_dropDown.bind()

    def menu_update(self, text, menu):
        self.menu_dropDown.dismiss()
        new_ep = list()
        for i in self.ep:
            if text in i:
                new_ep.append(i)
        menu_items = [{"viewclass": "OneLineListItem", "text": f"{i}", 
                            "font_style": "H5", "theme_text_color": "Custom", "text_color": [1, 1, 1, 1], 
                            "bg_color": '#153788', "on_release": partial(self.cb_menu, f"{i}", menu)} for i in new_ep]
        self.menu_dropDown.items = menu_items
        if menu == "cpf":
            self.menu_dropDown.caller = self.ids.cpf
        elif menu == "cidade":
            self.menu_dropDown.caller = self.ids.city
        elif menu == "cliente":
            self.menu_dropDown.caller = self.ids.name
        elif menu == "agente":
            self.menu_dropDown.caller = self.ids.agent
        self.menu_dropDown.open()

    def cb_menu(self, text, menu):
        if menu == "cpf":
            self.ids.cpf.text = text
        elif menu == "cidade":
            self.ids.city.text = text
        elif menu == "cliente":
            self.ids.name.text = text
        elif menu == "agente":
            self.ids.agent.text = text
        self.menu_dropDown.dismiss()

    def loadingClients(self):
        for _ in range(10):
            client = Client(ImageLeftWidget(source="images/icons/client.png"), RightCheckbox())
            client.id = f"{_}"
            client.text = "George Uamirim Rodriges da Silva"
            client.secondary_text = "123.456.789-10"
            client.tertiary_text = "Recife, rua das flores, numero tal, bairro tal"
            self.ids.list_clients.add_widget(client)

    def on_active(self, segmented_control: MDSegmentedControl, segmented_item: MDSegmentedControlItem) -> None:
        if "Todos" in segmented_item.text:
            self.ids.opone.text = "[color=153788]Todos[/color]"
            self.ids.optwo.text = "[color=fff]Restritos[/color]"
            self.ids.opthree.text = "[color=fff]Irrestritos[/color]"
            self.fast_search = segmented_item.text
        elif "Restritos" in segmented_item.text:
            self.ids.opone.text = "[color=fff]Todos[/color]"
            self.ids.optwo.text = "[color=153788]Restritos[/color]"
            self.ids.opthree.text = "[color=fff]Irrestritos[/color]"
            self.fast_search = segmented_item.text
        elif "Irrestritos" in segmented_item.text:
            self.ids.opone.text = "[color=fff]Todos[/color]"
            self.ids.optwo.text = "[color=fff]Restritos[/color]"
            self.ids.opthree.text = "[color=153788]Irrestritos[/color]"
            self.fast_search = segmented_item.text

    def backScreen(self, *args):
        pass

    def removes_marks_all_chips(self, selected_instance_chip):
        for instance_chip in self.ids.chip_box.children:
            if instance_chip != selected_instance_chip:
                instance_chip.active = False

    def on_save(self, instance, value, date_range):
        date = str(value).split("-")
        date_formated = f"{date[2]}/{date[1]}/{date[0]}"
        if self.is_start:
            self.ids.date_start.text = date_formated
        else:
            self.ids.date_end.text = date_formated

    def on_cancel(self, instance, value):
        if self.is_start:
            self.ids.date_start.text = ""
        else:
            self.ids.date_end.text = ""

    def consult(self):
        if self.fast_search is not None:
            self.loadingClients()

    def loading(self):
        self.ids.loading.active = not self.ids.loading.active

    def show_date_picker(self, id):
        self.is_start = True if id == "start" else False
        date_dialog = MDDatePicker(
            title_input="INSIRA UMA DATA",
            title="ESCOLHA UMA DATA"
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
