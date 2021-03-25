from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2


class OpenCVImage(Image):
    def __init__(self, **kwargs):
        super(OpenCVImage, self).__init__(**kwargs)

    def set_frame(self, frame, **kwargs):
        colorfmt = kwargs.get('colorfmt', 'bgr')

        # Converting the OpenCV buffer to a texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt=colorfmt
        )
        image_texture.blit_buffer(buf, colorfmt=colorfmt, bufferfmt=kwargs.get('bufferfmt', 'ubyte'))
        # Displaying the image from the texture
        self.texture = image_texture
