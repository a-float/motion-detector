import os

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.properties import BooleanProperty, ObjectProperty
from motion_lib import MotionTracker
from ui import CameraFeedScreen, DetectorSettingsPanel, DebugPanel, MaskPainterScreen
from ui.opencv_image import opencv_to_texture
import numpy as np
import cv2 as cv2

kivy.require('2.0.0')

FPS = 60


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class AppHeader(StackLayout):
    def __init__(self, handle_debug_mode, handle_edit_mask, show_load, open_camera, **kwargs):
        super(AppHeader, self).__init__(**kwargs)

        self.handle_debug_mode = handle_debug_mode
        self.handle_edit_mask = handle_edit_mask
        self.show_load = show_load
        self.open_camera = open_camera


class FeedWindow(BoxLayout):
    debug_mode = BooleanProperty(False)
    loadfile = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(FeedWindow, self).__init__(**kwargs)
        self.mt = MotionTracker()  # no args, gets the default ones

        self._setup_layout()
        self._popup = None

        self.interval_handle = Clock.schedule_interval(self.update, 1.0 / FPS)

    def _setup_layout(self):
        def toggle_debug():
            self.debug_mode = not self.debug_mode

        def handle_set_mask(mask_texture):
            npbuffer = np.frombuffer(mask_texture.pixels, np.uint8)
            height, width = mask_texture.height, mask_texture.width
            npbuffer = npbuffer.reshape(height, width, 4)
            gray = cv2.cvtColor(npbuffer, cv2.COLOR_BGR2GRAY)

            self.mt.set_mask(gray)

            self._mask_edit_popup.dismiss()
            self._mask_edit_popup = None

        def toggle_mask_edit():
            if self._mask_edit_popup is not None:
                self._mask_edit_popup.dismiss()
                self._mask_edit_popup = None
            else:
                mask_texture = opencv_to_texture(self.mt.get_mask(), colorfmt='luminance')
                content = MaskPainterScreen(mask_texture=mask_texture, handle_set_mask=handle_set_mask)
                self._mask_edit_popup = Popup(title="Edit mask", content=content, size_hint=(1, 1))
                self._mask_edit_popup.open()

        # Header
        self._app_header = AppHeader(
            handle_debug_mode=toggle_debug,
            handle_edit_mask=toggle_mask_edit,
            open_camera=self.open_camera,
            show_load=self.show_load
        )
        self.add_widget(self._app_header)

        # Middle content
        self._horizontal_box = BoxLayout()
        self.add_widget(self._horizontal_box)

        self._camera_feed_screen = CameraFeedScreen()
        self._horizontal_box.add_widget(self._camera_feed_screen)

        self._settings_panel = DetectorSettingsPanel(on_param_change=self._on_param_change)
        self._horizontal_box.add_widget(self._settings_panel)

        # Setting up the hidden debug panel
        self._debug_panel = DebugPanel()

        # Mask edit popup
        self._mask_edit_popup = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load video file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        vid = os.path.join(path, filename[0])
        if vid is not None and len(vid) > 0:
            if self.mt.is_capturing():
                self.mt.stop_capture()
            self.mt.start_capture(vid)

        self.dismiss_popup()

    def open_camera(self):
        if self.mt.is_capturing():
            self.mt.stop_capture()
        self.mt.start_capture()

    def update(self, dt):
        if not self.mt.is_capturing():
            return

        frame = self.mt.read_frame()

        parsed_frame = self.mt.parse_frame(frame)
        delta_frame, bit_frame, is_motion = self.mt.detect(parsed_frame, frame)  # draws at the second argument

        self.mt.show_time(frame)
        self.mt.save_motion(frame, is_motion)  # possibly starts the recorder, saves the frame

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
