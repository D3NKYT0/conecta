from kivymd.uix.screen import MDScreen
from kivy.app import App

try:
    import pyi_splash  # essa importação é referente ao PYINSTALLER (nao precisa ser instalada)
except:
    pass


class StartScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_pre_enter(self, *args):
        try:
            pyi_splash.close()
        except:
            pass
        return super().on_pre_enter(*args)

    def login(self):
        App.get_running_app().manager.current = 'login'
        App.get_running_app().manager.get_screen('login')
