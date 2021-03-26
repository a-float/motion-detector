from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2


def opencv_to_texture(buffer, **kwargs):
    colorfmt = kwargs.get('colorfmt', 'bgr')
    bufferfmt = kwargs.get('bufferfmt', 'ubyte')

    # Converting the OpenCV buffer to a texture
    buf1 = cv2.flip(buffer, 0)
    buf = buf1.tostring()
    image_texture = Texture.create(
        size=(buffer.shape[1], buffer.shape[0]),
        colorfmt=colorfmt
    )

    image_texture.blit_buffer(buf, colorfmt=colorfmt, bufferfmt=bufferfmt)
    return image_texture


class OpenCVImage(Image):
    def __init__(self, **kwargs):
        super(OpenCVImage, self).__init__(**kwargs)

    def set_frame(self, frame, **kwargs):
        # Displaying the image from the texture
        self.texture = opencv_to_texture(frame, **kwargs)
