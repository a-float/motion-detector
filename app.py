import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import BooleanProperty
from motion_lib import MotionTracker
from ui import CameraFeedScreen, DetectorSettingsPanel, DebugPanel

kivy.require('2.0.0')

FPS = 60


class AppHeader(StackLayout):
    def __init__(self, handle_debug_mode, handle_edit_mode, **kwargs):
        super(AppHeader, self).__init__(**kwargs)

        self.handle_debug_mode = handle_debug_mode
        self.handle_edit_mode = handle_edit_mode


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
    debug_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(FeedWindow, self).__init__(**kwargs)
        self.mt = MotionTracker()  # no args, gets the default ones
        self.mt.start_capture()

        self._setup_layout()

        self.interval_handle = Clock.schedule_interval(self.update, 1.0 / FPS)

    def _setup_layout(self):
        def toggle_debug():
            self.debug_mode = not self.debug_mode

        def toggle_mask_edit():
            pass

        self._app_header = AppHeader(handle_debug_mode=toggle_debug, handle_edit_mode=toggle_mask_edit)
        self.add_widget(self._app_header)

        self._horizontal_box = BoxLayout()
        self.add_widget(self._horizontal_box)

        self._camera_feed_screen = CameraFeedScreen()
        self._horizontal_box.add_widget(self._camera_feed_screen)

        self._settings_panel = DetectorSettingsPanel(on_param_change=self._on_param_change)
        self._horizontal_box.add_widget(self._settings_panel)

        # Setting up the hidden debug panel
        self._debug_panel = DebugPanel()

    def update(self, dt):
        frame = self.mt.read_frame()

        parsed_frame = self.mt.parse_frame(frame)
        delta_frame = self.mt.calc_diff(parsed_frame)
        bit_frame = self.mt.calc_bit(delta_frame)

        self.mt.show_time(frame)
        self.mt.show_contours(frame, parsed_frame, bit_frame)

        self._camera_feed_screen.set_frame(frame)

        self._debug_panel.set_step('Parsed frame', parsed_frame, colorfmt='luminance')
        self._debug_panel.set_step('Delta frame', delta_frame, colorfmt='luminance')
        self._debug_panel.set_step('Thresh frame', bit_frame, colorfmt='luminance')

    def _on_param_change(self, param_key, value):
        params = self.mt.get_params()

        params[param_key] = value
        self.mt.set_params(params)
        pass

    def on_debug_mode(self, instance, value):
        if value:
            self._horizontal_box.add_widget(self._debug_panel, 2)
        else:
            self._horizontal_box.remove_widget(self._debug_panel)


class MotionDetectorApp(App):
    def build(self):
        return FeedWindow()


if __name__ == '__main__':
    MotionDetectorApp().run()
