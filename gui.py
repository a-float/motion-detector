import PySimpleGUI as sg
import numpy as np
import imutils
import cv2
# DEF_ARGS should be given some accessor functions so that one can't modify it by accident
from motion_lib import DEFAULT_PARAMS
from gui_mask import GUIMaskPainter

BTN_EXIT = 'exit'
BTN_INIT = 'init'
BTN_RECORD = 'record'
BTN_STOP = 'stop'
BTN_DEBUG = 'debug'
BTN_CREATE_MASK = 'Create mask'

DEBUG_IMG_SIZE = (300, 200)


# hardcoded size, works for my webcam
# updates the image with the key that's in the window
# if image is not specified, draws a black square
def update_sg_image(window, key, image=None, size=(480, 360)):
    if image is None:
        image = np.zeros((size[1], size[0], 3), np.uint8)
    else:
        # imutils.resize does not take height argument, it always preserved the xy-ratio
        image = imutils.resize(image, width=size[0])

    # image = cv2.resize(image, size, interpolation = cv2.INTER_AREA)
    img_bytes = cv2.imencode('.png', image)[1].tobytes()
    window[key].update(data=img_bytes)
    pass


# updates label image pair in the specified debug window
def update_debug_panel(d_window, img_key=None, image=None, text_key=None, text=''):
    if img_key:
        update_sg_image(d_window, img_key, image, size=DEBUG_IMG_SIZE)
    if text_key:
        d_window[text_key].update(value=text)


def create_main_window():
    menu_def = [
        ['&Mask', [BTN_CREATE_MASK]]
    ]

    # define the window layout
    layout = [[sg.Menu(menu_def)],
              [sg.Text('Motion-Detector', size=(50, 1), justification='center', font='Helvetica 20')],
              [
                  sg.Column(
                      [
                          [sg.Image(key='image')],
                          [
                              sg.Button('Init', size=(7, 1), font='Helvetica 14', key=BTN_INIT),
                              sg.Button('Record', size=(7, 1), font='Helvetica 14', key=BTN_RECORD),
                              sg.Button('Stop', size=(7, 1), font='Helvetica 14', key=BTN_STOP),
                              sg.Button('Debug', size=(7, 1), font='Helvetica 14', key=BTN_DEBUG),
                              sg.Button('Exit', size=(7, 1), font='Helvetica 14', key=BTN_EXIT),
                          ]
                      ],
                      element_justification='center',
                      vertical_alignment='top'
                  ),
                  sg.Column(
                      [
                          [sg.Text('Parameters')],
                          *[  # unpacking
                              [
                                  sg.Text(v[0], size=(10, 1)),  # param name
                                  sg.Slider(range=(1, v[1] * 2),  # arbitrary range
                                            default_value=v[1],  # param value
                                            size=(30, 10),
                                            orientation="h",
                                            enable_events=True,
                                            # resolution=1 if 'blur' not in v[0] else 2,  #blur has to be odd
                                            key="slider:" + str(v[0]))
                              ]
                              for v in DEFAULT_PARAMS.items()
                          ]
                      ],
                      vertical_alignment='top'
                  )
              ]  # end of column row
              ]  # end of layout

    return sg.Window('MotionTrackerGui', layout, location=(500, 200), finalize=True)


def create_debug_window():
    debug_layout = [
        [sg.Text('long image name 1', k='text1')],
        [sg.Image(k='img1')],
        [sg.Text('long image name 1', k='text2')],
        [sg.Image(k='img2')],
        [sg.Text('long image name 1', k='text3')],
        [sg.Image(k='img3')],
    ]

    win = sg.Window('Debug window', debug_layout, finalize=True, location=(50, 20))
    update_sg_image(win, 'img1', size=DEBUG_IMG_SIZE)
    update_sg_image(win, 'img2', size=DEBUG_IMG_SIZE)
    update_sg_image(win, 'img3', size=DEBUG_IMG_SIZE)
    return win


class GUI:
    def __init__(self, handle_record, handle_stop, handle_update, handle_param_update):
        sg.theme('Black')
        self.main_window = create_main_window()
        self.handle_record = handle_record
        self.handle_stop = handle_stop
        self.handle_update = handle_update
        self.handle_param_update = handle_param_update

        self.mask_painter = GUIMaskPainter()
        self.debug_window = None

        # Initializing a black screen for a start.
        self.update_feed_image()

    def run(self):
        running = True

        while running:
            event, values = self.main_window.read(timeout=20)  # refresh every 20ms
            if event in (sg.WIN_CLOSED, BTN_EXIT):
                running = False
            elif event == BTN_RECORD:
                self.handle_record()
            elif event == BTN_STOP:
                self.handle_stop()
                self.update_feed_image()
            elif event == BTN_DEBUG:
                if not self.debug_window:
                    self.debug_window = create_debug_window()
            elif event == BTN_CREATE_MASK:
                self.mask_painter.show()
            elif event.split(':')[0] == 'slider':  # slider keys are in format slider:[param_name]
                param_name = event.split(':')[1]

                # fix for the blur values. A slider with resolution 2 only takes even values
                # cv2 blur function needs an odd one
                if 'blur' in param_name and values[event] % 2 == 0:
                    self.main_window[event].update(value=values[event] + 1)
                    values[event] += 1

                self.handle_param_update(param_name, int(values[event]))

            self.mask_painter.update()
            self.handle_update(self)
            # end while

        # Deallocating unused resources
        self.mask_painter.close()
        self.main_window.close()

    # hardcoded size, works for my webcam
    # updates the image with the key that's in the window
    # if image is not specified, draws a black square
    def update_feed_image(self, image=None, size=(480, 360)):
        update_sg_image(self.main_window, 'image', image, size)

    def update_debug_panel(self, key, image, title_key, title):
        if self.debug_window is not None:
            update_debug_panel(self.debug_window, key, image, title_key, title)
