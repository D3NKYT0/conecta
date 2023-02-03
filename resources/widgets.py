from kivy.uix.label import Label

from kivy.clock import Clock
from datetime import datetime

from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout


class ClockRealTime(Label):
    def __init__(self, widget, **kwargs):
        self._trigger = Clock.create_trigger(self.start)
        super(ClockRealTime, self).__init__(**kwargs)
        self.bind(x=self._trigger, y=self._trigger)

        self.dt_atual = datetime.now()
        self.hour = self.dt_atual.strftime('%H:%M:%S')
        self.date = self.dt_atual.strftime('%d/%m/%Y')

        self.widget = widget

    def start(self, *largs):
        Clock.schedule_interval(self.clock_now, 1)
        return self

    def clock_now(self, dt):
        self.dt_atual = datetime.now()
        self.hour = self.dt_atual.strftime('%H:%M:%S')
        self.date = self.dt_atual.strftime('%d/%m/%Y')

        self.widget.ids.data.text = self.date
        self.widget.ids.hora.text = self.hour


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''


class RightContainer(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True
