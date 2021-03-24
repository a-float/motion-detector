from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import (
    ObjectProperty
)
import cv2

FPS = 60


class CameraFeed(Image):
    capture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CameraFeed, self).__init__(**kwargs)

        self.interval_handle = Clock.schedule_interval(self.update, 1.0 / FPS)

    def update(self, dt):
        if self.capture is None:
            return

        frame = self.capture.read()
        # Converting the OpenCV buffer to a texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # Displaying the image from the texture
        self.texture = image_texture


class CameraFeedScreen(Widget):
    def __init__(self, **kwargs):
        super(CameraFeedScreen, self).__init__(**kwargs)
