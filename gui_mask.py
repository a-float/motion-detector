import PySimpleGUI as sg
from tkinter import PhotoImage
from math import ceil, sqrt

DEFAULT_MASK_BRUSH_SIZE = 5
FALLOFF_THRESHOLD = 0.5


def clerp(a, b, t):
    return ceil(a * (1 - t) + b * t)


class GUIMaskPainter:
    def __init__(self, size=(128, 128)):
        self.brush_size = 5
        self.canvas_size = size

        self.layout = [
            [sg.Canvas(size=size, key='mask_canvas')],
            [sg.Slider(range=(1, 40), default_value=DEFAULT_MASK_BRUSH_SIZE,
                       size=(30, 10),
                       orientation="h",
                       key='rad_slider',
                       enable_events=True)
             ]
        ]

        self.window = None
        self.canvas_image = None

    # bound to the mask canvas object. Should be used to create the mask.
    # not so easy to extract the image :/
    # TODO add alpha coloring. Its not supported by tkinter so i has to be via creating a separate image
    # preferably with Pillow, then set its alpha and draw the new image instead
    def canvas_draw_callback(self, event, brush_color):
        if self.canvas_image is None:
            return

        full_r = ceil(self.brush_size)
        r = ceil(full_r * (1 - FALLOFF_THRESHOLD))
        falloff_r = full_r - r

        center = (int(event.x), int(event.y))
        bound_min = (max(0, center[0] - full_r), max(0, center[1] - full_r))
        bound_max = (min(center[0] + full_r, self.canvas_size[0] - 1),
                     min(center[1] + full_r, self.canvas_size[1] - 1))

        for x in range(bound_min[0], bound_max[0] + 1):
            for y in range(bound_min[1], bound_max[1] + 1):
                bg_color = self.canvas_image.get(x, y)
                dist = sqrt((center[0] - x) ** 2 + (center[1] - y) ** 2)

                opacity = 0.0

                if dist < r:
                    opacity = 1.0
                elif falloff_r > 0:
                    opacity = 1.0 - (dist - r) / falloff_r

                opacity = max(0.0, min(opacity, 1.0))

                color = (
                    clerp(bg_color[0], brush_color[0], opacity),
                    clerp(bg_color[1], brush_color[1], opacity),
                    clerp(bg_color[2], brush_color[2], opacity)
                )
                self.canvas_image.put("#%02x%02x%02x" % color, (x, y))

        # print("clicked at", event.x, event.y)

    def show(self):
        if self.window is not None:
            return

        self.window = sg.Window('Create mask window', self.layout, finalize=True)
        tk_canvas = self.window['mask_canvas'].tk_canvas
        tk_canvas.bind("<B1-Motion>", lambda event: self.canvas_draw_callback(event, (255, 255, 255)))  # lmb drag
        tk_canvas.bind("<Button-1>", lambda event: self.canvas_draw_callback(event, (255, 255, 255)))  # lmb click
        tk_canvas.bind("<B3-Motion>", lambda event: self.canvas_draw_callback(event, (0, 0, 0)))  # rmb drag
        tk_canvas.bind("<Button-3>", lambda event: self.canvas_draw_callback(event, (0, 0, 0)))  # rmb click

        tk_canvas.pack()

        self.canvas_image = PhotoImage(width=self.canvas_size[0], height=self.canvas_size[1])
        tk_canvas.create_image((self.canvas_size[0]/2, self.canvas_size[1]/2), image=self.canvas_image, state="normal")

    def close(self):
        if self.window is not None:
            self.window.close()
            self.window = None

    def update(self):
        if self.window is None:
            return

        event, values = self.window.read()

        if event is sg.WIN_CLOSED:
            self.close()
        elif event == 'rad_slider':
            self.brush_size = values[event]
