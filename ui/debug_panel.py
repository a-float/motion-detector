from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from motion_lib import PARAMETERS
from .opencv_image import OpenCVImage


class Step(BoxLayout):
    def __init__(self, label='Step', **kwargs):
        super(Step, self).__init__(**kwargs)

        self.orientation = 'vertical'

        self.label = Label(text=label, size_hint=(1, None), height=40)
        self.add_widget(self.label)

        self.image = OpenCVImage()
        self.add_widget(self.image)

    def set_frame(self, frame, **kwargs):
        self.image.set_frame(frame, **kwargs)


class DebugPanel(BoxLayout):
    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.steps = {}

    def set_step(self, key, frame, **kwargs):
        step = self.steps.get(key, None)

        if step is None:
            step = Step(label=key)
            self.add_widget(step)
            self.steps[key] = step

        step.set_frame(frame, **kwargs)
