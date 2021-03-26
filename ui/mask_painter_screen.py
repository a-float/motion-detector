from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle


class CanvasWrapper(Widget):
    def __init__(self, mask_texture, **kwargs):
        super(CanvasWrapper, self).__init__(**kwargs)

        self.mask_texture = mask_texture
        self.brush_size = 5
        self.intensity = 1

        self.refresh_canvas()
        self.bind(pos=self.refresh_canvas, size=self.refresh_canvas)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return

        with self.canvas:
            Color(self.intensity, self.intensity, self.intensity, 1)
            d = self.brush_size
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.brush_size)

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        # Redrawing the mask image on top to get rid of the overflowing bits.
        self.mask_texture = self.export_as_image().texture
        self.refresh_canvas()

    def refresh_canvas(self, instance=None, value=None):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.mask_texture, pos=(self.x, self.y + self.height), size=(self.width, -self.height))


class ToolWrapper(BoxLayout):
    def __init__(self, label, slider, **kwargs):
        super(ToolWrapper, self).__init__(**kwargs)

        self.orientation = 'vertical'

        self.label = Label(text=label)
        self.add_widget(self.label)

        self.add_widget(slider)


class MaskPainterScreen(BoxLayout):
    def __init__(self, mask_texture, handle_set_mask, **kwargs):
        super(MaskPainterScreen, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.padding = (10, 10)

        # Upper box
        self.upper_box = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(self.upper_box)

        self.canvas_wrapper = CanvasWrapper(mask_texture, size=mask_texture.size, size_hint=(None, None))
        self.upper_box.add_widget(self.canvas_wrapper)

        # Tools
        self.tools_box = StackLayout(orientation='tb-lr', size_hint=(1, None), height=40, spacing=(10, 0))
        self.add_widget(self.tools_box)

        def handle_size_change(instance, value):
            self.canvas_wrapper.brush_size = value

        def handle_intensity_change(instance, value):
            self.canvas_wrapper.intensity = value

        def handle_apply_changes(instance):
            handle_set_mask(self.canvas_wrapper.export_as_image().texture)

        size_slider = Slider(min=5, max=50)
        size_tool = ToolWrapper('Size', size_slider, size_hint=(None, 1), width=200)
        self.tools_box.add_widget(size_tool)
        size_slider.bind(value=handle_size_change)

        intensity_slider = Slider(min=0.0, max=1.0, value=1.0)
        intensity_tool = ToolWrapper('Intensity', intensity_slider, size_hint=(None, 1), width=200)
        self.tools_box.add_widget(intensity_tool)
        intensity_slider.bind(value=handle_intensity_change)

        apply_button = Button(text="Apply changes", on_press=handle_apply_changes, width=250, size_hint=(None, 1))
        self.tools_box.add_widget(apply_button)


