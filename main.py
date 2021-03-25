from motion_lib import MotionTracker
from gui import GUI


def main():
    recording = False
    mt = MotionTracker()  # no args, gets the default ones

    def handle_record():
        nonlocal recording

        if mt.is_capturing():
            recording = not recording

    def handle_stop():
        nonlocal recording

        if mt.is_capturing():
            mt.stop_capture()
            recording = False

    def handle_update(ui: GUI):
        if recording:
            frame = mt.read_frame()
            parsed_frame = mt.parse_frame(frame)
            delta_frame = mt.calc_diff(parsed_frame)
            bit_frame = mt.calc_bit(delta_frame)

            mt.show_time(frame)
            mt.show_contours(frame, parsed_frame, bit_frame)
            ui.update_feed_image(frame, size=(480, 600))
            # update_sgimage(main_window, 'image', frame, size=(480, 600))

            # TODO the update_debug_panel may be more concise
            ui.update_debug_panel('img1', parsed_frame, 'text1', 'Parsed frame')
            ui.update_debug_panel('img2', delta_frame, 'text2', 'Delta frame')
            ui.update_debug_panel('img3', bit_frame, 'text3', 'Tresh frame')

    def handle_param_update(param_name, value):
        params = mt.get_params()
        if param_name not in params:
            raise NameError(f'No OpenCV parameter found with the name "{param_name}"')

        params[param_name] = value
        mt.set_params(params)

    gui = GUI(handle_record=handle_record,
              handle_stop=handle_stop,
              handle_update=handle_update,
              handle_param_update=handle_param_update)

    if not mt.is_capturing():
        mt.start_capture()

    # Running the main event loop
    gui.run()

    # Stopping capture after getting out of the main loop
    if mt.is_capturing():
        mt.stop_capture()


if __name__ == '__main__':
    main()
