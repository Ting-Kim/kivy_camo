import sys
import os
import time
import datetime
import cv2
import numpy as np
from PIL import Image
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture

ROOT_DIR = os.path.abspath("")
sys.path.append(ROOT_DIR)
from Mask_RCNN.demo import ImageProcess


def export_to_png(self, filename, *args):
    """Saves an image of the widget and its children in png format at the
    specified filename. Works by removing the widget canvas from its
    parent, rendering to an :class:`~kivy.graphics.fbo.Fbo`, and calling
    :meth:`~kivy.graphics.texture.Texture.save`.
    .. note::
        The image includes only this widget and its children. If you want to
        include widgets elsewhere in the tree, you must call
        :meth:`~Widget.export_to_png` from their common parent, or use
        :meth:`~kivy.core.window.Window.screenshot` to capture the whole
        window.
    .. note::
        The image will be saved in png format, you should include the
        extension in your filename.
    .. versionadded:: 1.8.1
    """

    if self.parent is not None:
        canvas_parent_index = self.parent.canvas.indexof(self.canvas)
        self.parent.canvas.remove(self.canvas)

    fbo = Fbo(size=self.size)

    with fbo:
        ClearColor(0, 0, 0, 1)
        ClearBuffers()
        Translate(-self.x, -self.y, 0)

    fbo.add(self.canvas)
    fbo.draw()
    fbo.texture.save(filename)
    fbo.remove(self.canvas)

    if self.parent is not None:
        self.parent.canvas.insert(canvas_parent_index, self.canvas)

    return True


class MirrorCamera(Camera):
    def _camera_loaded(self, *largs):
        self.texture = self._camera.texture
        self.texture_size = list(self.texture.size)
        self.texture.flip_vertical()


class CameraWidget(BoxLayout):
    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename="test2.png")
        print("Captured")


class Demo(ScreenManager):

    # after improve
    def capture(self, *args):
        # select instance for id from demo.kv
        camera = self.ids.camera1
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = "IMG_{}.png".format(timestr)
        img = camera.export_as_image(file_name)
        now = datetime.datetime.now()
        print(now)
        # kivi.core.image.Image to kivy.graphics.texture.Texture
        texture_of_image = img.texture
        texture_height, texture_width = texture_of_image.height, texture_of_image.width

        # kivy.graphics.texture.Texture to numpy.ndarray
        newvalue = np.frombuffer(texture_of_image.pixels, np.uint8)
        newvalue = newvalue.reshape(texture_height, texture_width, 4)

        # Image processing
        imageProcess = ImageProcess(file_name, newvalue)
        blurred_image = imageProcess.adapt_blur()
        print(datetime.datetime.now() - now )
        print("Captured")

    """
    # before improve
    def capture(self, *args):
        camera = self.ids.camera1
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = "IMG_{}.png".format(timestr)
        camera.export_to_png(file_name)
        imageProcess = ImageProcess(file_name)
        blurred_image = imageProcess.adapt_blur()
        print("Captured")
    """


class DemoApp(App):
    def build(self):
        return Demo()


# PIL.Image object to numpy.ndarray object, by Taeho
def numpy_to_image(numpy_img):
    img = Image.fromarray(numpy_img, "RGB")
    return img


def pil_image_to_base64(pil_img):
    data = BytesIO()
    pil_img.save(data, "png")  # pick your format
    # pil_img.save("uploads/images/test.png", "png")
    pil_img.seek(0)
    data64 = base64.b64encode(data.getvalue())
    return data64.decode("utf-8")


DemoApp().run()
