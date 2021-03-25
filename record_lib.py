import cv2
from time import gmtime, strftime


class Record:
    def __init__(self, fps, resolution_x=640, resolution_y=480):
        """This class allow to record"""
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')  # codec
        self.fps = fps
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.out_file_name = 'output.avi'
        self.out = cv2.VideoWriter(self.out_file_name, self.fourcc, self.fps, (self.resolution_x, self.resolution_y))

    def start(self):
        self.out_file_name = strftime("%d-%b-%Y_%H:%M:%S", gmtime())

    def save_frame(self, frame):
        self.out.write(frame)

    # def end(self):
    #     self.out.release()
