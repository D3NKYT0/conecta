from kivymd.uix.screen import MDScreen
from kivy.app import App


class StartScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def login(self):
        App.get_running_app().manager.current = 'login'
        App.get_running_app().manager.get_screen('login')
