import PySimpleGUI as sg
import cv2
import numpy as np
from motion_lib import MotionTracker
#DEF_ARGS should be given some accesor functions so that one cant't modify it by accident
from motion_lib import DEF_ARGS 
import imutils

mask_drawing_radius = 5
DEBUG_IMG_SIZE = (300,200)

#hardcoded size, works for my webcam
#updates the image with the key thats in the window
#if image is not specified, draws a black square
def update_sgimage(window, key, image=None, size=(480, 360)):
    if image is None:
        image = np.zeros((size[1], size[0], 3), np.uint8)
    else:
         #imutils.resize does not take height argument, it always preserved xyratio
         image = imutils.resize(image, width=size[0])
        # image = cv2.resize(image, size, interpolation = cv2.INTER_AREA)
    imgbytes = cv2.imencode('.png', image)[1].tobytes()
    window[key].update(data=imgbytes)

#updates label image pair in the specified debug window
def update_debug_panel(d_window, img_key=None, image=None, text_key=None, text=''):
    if img_key:
        update_sgimage(d_window, img_key, image, size=DEBUG_IMG_SIZE)
    if text_key:
        d_window[text_key].update(value=text)

#binded to the mask canvas object. Should be used to create the mask.
#not so easy to extract the image :/
#TODO add alpha coloring. Its not supported by tkinter so i has to be via creating a separate image
#preferably with Pillow, then set its alpha and draw the new image instead
def canvas_draw_callback(event, mask_win, color):
    tk_canvas = mask_win['mask_canvas'].tk_canvas
    r = mask_drawing_radius
    tk_canvas.create_oval(event.x-r, event.y-r, event.x+r, event.y+r, fill=color, outline='')
    tk_canvas.pack()
    # print("clicked at", event.x, event.y)

def create_mask_window():
    layout = [
                [sg.Canvas(size=(400,400), key='mask_canvas')],
                [sg.Slider(range=(1, 40), default_value=mask_drawing_radius, 
                                size=(30, 10),
                                orientation="h", 
                                key='rad_slider',
                                enable_events=True)
                ]
             ]
    win = sg.Window('Create mask window', layout, finalize = True)
    tk_canvas = win['mask_canvas'].tk_canvas
    tk_canvas.bind("<B1-Motion>", lambda event: canvas_draw_callback(event, win, 'red')) #left mb drag
    tk_canvas.bind("<B3-Motion>", lambda event: canvas_draw_callback(event, win, 'black')) #right mb drag
    tk_canvas.pack()

    return win

def create_debug_window():
    debug_layout = [
                    [sg.Text('long image name 1',k='text1')],
                    [sg.Image(k='img1')],
                    [sg.Text('long image name 1',k='text2')],
                    [sg.Image(k='img2')],
                    [sg.Text('long image name 1',k='text3')],
                    [sg.Image(k='img3')],
                   ]

    win = sg.Window('Debug window', debug_layout, finalize=True, location=(50,20))
    update_sgimage(win, 'img1', size=DEBUG_IMG_SIZE)
    update_sgimage(win, 'img2', size=DEBUG_IMG_SIZE)
    update_sgimage(win, 'img3', size=DEBUG_IMG_SIZE)
    return win

def create_main_window():
    menu_def =  [
                    ['&Mask', ['Create mask']] 
                ]
    # define the window layout
    layout = [  [sg.Menu(menu_def)],
                [sg.Text('OpenCV Demo', size=(50, 1), justification='center', font='Helvetica 20')],
                [
                sg.Column(
                    [
                        [sg.Image(key='image')],
                        [
                            sg.Button('Init', size=(7, 1), font='Helvetica 14'),
                            sg.Button('Play', size=(7, 1), font='Helvetica 14'),
                            sg.Button('Stop', size=(7, 1), font='Helvetica 14'),
                            sg.Button('Debug', size=(7, 1), font='Helvetica 14'),
                            sg.Button('Exit', size=(7, 1), font='Helvetica 14'), 
                        ]
                    ],
                    element_justification='center',
                    vertical_alignment='top'
                ),
                sg.Column(
                        [
                            [sg.Text('Parameters')],
                            *[#unpacking
                                [
                                sg.Text(v[0], size=(10,1)),  #param name
                                sg.Slider(range=(1, v[1]*2), #arbitrary range
                                    default_value=v[1],     #param value
                                    size=(30, 10), 
                                    orientation="h",
                                    enable_events=True,
                                    # resolution=1 if 'blur' not in v[0] else 2,  #blur has to be odd
                                    key="slider:"+str(v[0]))
                                ]
                                for v in DEF_ARGS.items()
                            ]
                        ],
                        vertical_alignment='top'
                    )
                ] #end of column row
            ] #end of layout

    return sg.Window('MotionTrackerGui', layout, location=(500, 200), finalize = True)

#main loop
def main(): #TODO maybe move the layouts to a separate file
    sg.theme('Black')
    #dummy menu except for the canvas
    main_window = create_main_window()
    update_sgimage(main_window, 'image')
    debug_window = None
    mask_window = None

    recording = False
    mt = MotionTracker() #no args, gets the default ones

    while True:
        window, event, values = sg.read_all_windows(timeout=20) #refresh every 20ms

        if event == 'Exit' or event == sg.WIN_CLOSED:
            if window == main_window:
                if mt.is_capturing():
                    mt.stop_capture()
                window.close()
                return
            elif window == debug_window:
                window.close()
                debug_window = None
            elif window == mask_window:
                window.close()
                mask_window = None

        if window == main_window:
            if event == 'Init':
                if not mt.is_capturing():
                    mt.start_capture()
                    recording = True

            elif event == 'Play':
                if mt.is_capturing():
                    recording = not recording   

            elif event == 'Stop':
                if mt.is_capturing():
                    mt.stop_capture()
                    recording = False
                    update_sgimage(window, 'image')

            elif event == 'Debug':
                if not debug_window:
                    debug_window = create_debug_window()

            elif event == 'Create mask':
                if not mask_window:
                    mask_window = create_mask_window()

            #slider keys are in format slider:[param_name]
            elif event.split(':')[0] == 'slider':
                params = mt.get_params()
                param_name = event.split(':')[1]
                #fix for the blur values. A slider with resolution 2 only takes even values
                #cv2 blur function needs an odd one
                if 'blur' in param_name and values[event]%2==0: 
                    main_window[event].update(value = values[event]+1)
                    values[event]+=1

                params[param_name] = int(values[event])
                mt.set_params(params)

        elif window == mask_window:
            if event == 'rad_slider':
                global mask_drawing_radius
                mask_drawing_radius = values[event] 


        if recording:
            frame = mt.read_frame()
            parsed_frame = mt.parse_frame(frame)
            delta_frame = mt.calc_diff(parsed_frame)
            bit_frame = mt.calc_bit(delta_frame)
            
            mt.show_time(frame)
            mt.show_contours(frame, parsed_frame, bit_frame)
            update_sgimage(main_window, 'image', frame, size=(480, 600))
            
            if debug_window is not None:
                #TODO the update_debug_panel may be more concise
                update_debug_panel(debug_window, 'img1', parsed_frame, 'text1', 'Parsed frame')
                update_debug_panel(debug_window, 'img2', delta_frame, 'text2', 'Delta frame')
                update_debug_panel(debug_window, 'img3', bit_frame, 'text3', 'Tresh frame')

if __name__ == '__main__':
    main()