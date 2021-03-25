from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse
from kivy.graphics.texture import Texture
from kivy.properties import (
    ObjectProperty
)
import cv2


class CameraFeed(Image):
    def __init__(self, **kwargs):
        super(CameraFeed, self).__init__(**kwargs)

    def set_frame(self, frame):
        # Converting the OpenCV buffer to a texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # Displaying the image from the texture
        self.texture = image_texture


class CameraFeedScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraFeedScreen, self).__init__(**kwargs)

        self.camera_feed = CameraFeed()
        self.add_widget(self.camera_feed)

    def set_frame(self, frame):
        self.camera_feed.set_frame(frame)
