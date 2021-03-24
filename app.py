import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line

kivy.require('2.0.0')


class AppHeader(StackLayout):
    def __init__(self, **kwargs):
        super(AppHeader, self).__init__(**kwargs)


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


class MotionDetectorApp(App):
    def build(self):
        return FeedWindow()


if __name__ == '__main__':
    MotionDetectorApp().run()
