from kivy.app import App

from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import ThreeLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from resources import widgets, utils
from resources.widgets import *


class Client(ThreeLineAvatarIconListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClientScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        self.fast_search = "Todos"
        self.clock = widgets.ClockRealTime(widget=self).start()
        self.hardware = utils.getSystemInfo()
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
        App.get_running_app().manager.current = 'index'
        App.get_running_app().manager.get_screen('index')

    def removes_marks_all_chips(self, selected_instance_chip):
        for instance_chip in self.ids.chip_box.children:
            if instance_chip != selected_instance_chip:
                instance_chip.active = False

    def on_save(self, instance, value, date_range):
        date = str(value).split("-")
        date_formated = f"{date[2]}/{date[1]}/{date[0]}"
        self.ids.date.text = date_formated

    def on_cancel(self, instance, value):
        self.ids.date.text = ""

    def consult(self):
        if self.fast_search is not None:
            self.loadingClients()

    def loading(self):
        self.ids.loading.active = not self.ids.loading.active

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            title_input="INSIRA UMA DATA",
            title="ESCOLHA UMA DATA"
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
