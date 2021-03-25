import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from motion_lib import MotionTracker
from ui import CameraFeedScreen, DetectorSettingsPanel

kivy.require('2.0.0')

FPS = 60


class AppHeader(StackLayout):
    def __init__(self, **kwargs):
        super(AppHeader, self).__init__(**kwargs)

    def handle_edit_mask(self):
        print('WHAT')


class MaskPaintWidget(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 1, 0.5)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y))

        print(touch)

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]


class FeedWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(FeedWindow, self).__init__(**kwargs)
        self.mt = MotionTracker()  # no args, gets the default ones
        self.mt.start_capture()

        self._setup_layout()

        self.interval_handle = Clock.schedule_interval(self.update, 1.0 / FPS)

    def _setup_layout(self):
        self._app_header = AppHeader()
        self.add_widget(self._app_header)

        self._horizontal_box = BoxLayout()
        self.add_widget(self._horizontal_box)

        self._camera_feed_screen = CameraFeedScreen()
        self._horizontal_box.add_widget(self._camera_feed_screen)

        self._settings_panel = DetectorSettingsPanel(on_param_change=self._on_param_change)
        self._horizontal_box.add_widget(self._settings_panel)

    def update(self, dt):
        frame = self.mt.read_frame()

        parsed_frame = self.mt.parse_frame(frame)
        delta_frame = self.mt.calc_diff(parsed_frame)
        bit_frame = self.mt.calc_bit(delta_frame)

        self.mt.show_time(frame)
        self.mt.show_contours(frame, parsed_frame, bit_frame)

        self._camera_feed_screen.set_frame(frame)

    def _on_param_change(self, param_key, value):
        print(f'{param_key}: {value}')
        pass


class MotionDetectorApp(App):
    def build(self):
        return FeedWindow()


if __name__ == '__main__':
    MotionDetectorApp().run()
