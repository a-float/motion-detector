from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from motion_lib import PARAMETERS


class ParamSlider(Slider):
    def __init__(self, param_key, param, **kwargs):
        super(ParamSlider, self).__init__(**kwargs)

        self.param_key = param_key
        self.param = param


class DetectorSettingsPanel(GridLayout):
    def __init__(self, on_param_change, **kwargs):
        super(DetectorSettingsPanel, self).__init__(**kwargs)

        self.on_param_change = on_param_change

        for i, (key, parameter) in enumerate(PARAMETERS.items()):
            self.add_widget(Label(text=parameter.label, size_hint=(1, None), halign='left', text_size=(self.width, None)))

            slider = ParamSlider(
                key,
                parameter,
                min=parameter.min_value,
                max=parameter.max_value,
                value=parameter.default,
                size_hint=(1, None)
            )

            slider.bind(value=self.handle_value_change)

            self.add_widget(slider)

    def handle_value_change(self, instance, value):
        parsed_value = instance.param.parse(value)
        self.on_param_change(instance.param_key, parsed_value)
