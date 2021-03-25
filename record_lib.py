import cv2
from time import gmtime, strftime

class Recorder:
    def __init__(self, wait_time):
        """This class allows to record"""
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')  # codec
        self.fps = None
        self.res_x = None
        self.res_y = None
        self.out_file_name = 'output.avi'
        self.out = None
        self.wait_time = wait_time

    def _setup(self, fps, res_x, res_y):
        self.fps = fps
        self.res_x = res_x
        self.res_y = res_y

    def start(self, fps, res_x=640, res_y=480):
        if self.out is None:
            self._setup(fps, res_x, res_y)
            self.out_file_name = strftime("%d_%b_%Y_%H_%M_%S", gmtime())+".avi"
            print("Starting saving video to file {}".format(self.out_file_name))
            self.out = cv2.VideoWriter(self.out_file_name, self.fourcc, fps, (res_x, res_y))
        else:
            print("Cannot start an active recorder")
    
    def save_frame(self, frame):
        self.out.write(frame)

    def is_recording(self):
        return not self.out  is None

    def stop(self):
        if self.out is not None:
            print("End of video saving.")
            self.out.release()
            self.out = None
        else:
            print("Cannot stop an inactive recorder")
