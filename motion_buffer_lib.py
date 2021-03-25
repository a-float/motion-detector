from time import time


class MotionBuffer:
    def __init__(self, refresh_rate, frame):
        """refresh_rate is a list of times [s] at which to update the frame"""
        self.refresh_rate = refresh_rate
        self.size = len(refresh_rate)
        self.last_refresh = [time()] * self.size
        self.frame_buffer = [frame] * self.size
        self.is_change = 0

    def is_movement(self):
        if self.is_change:
            self.is_change = 0
            return 1
        return 0

    def update_buffer(self, frame):
        actual_time = time()

        for i in range(self.size):
            if actual_time - self.last_refresh[i] >= self.refresh_rate[i]:
                # compare with previous frame including opacity -> extract this method to new class / create diamond
                #   if motion_detected -> self.is_change = 1
                self.frame_buffer[i] = frame
                self.last_refresh[i] = actual_time

    # def get_buffer(self):
    #     return self.frame_buffer
    #
    # def get_refresh_rate(self):
    #     return self.refresh_rate
