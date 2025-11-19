import os


# Must come before kivy imports
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.clock import Clock  # noqa: E402
from kivy.properties import NumericProperty

class VirtualTankWidget(Widget):
    percent = NumericProperty(50)
    def __init__(self, **kwargs):
        super(VirtualTankWidget, self).__init__(**kwargs)


        self.level: float = 0.5

        Clock.schedule_interval(self.draw_water, 1/30)

        Builder.load_file(os.path.join(os.path.dirname(__file__), "res/tank.kv"))

    def set_percent(self, nieuw: float):
        self.percent = nieuw
        print(self.percent)

    def adjust_water(self, level: float) -> None:
        self.level = level /105
        self.percent = level

    def draw_water(self, dt: float):
        self.water_level = self.level





