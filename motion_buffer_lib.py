from time import time

class MotionBuffer:
    def __init__(self, frame, refresh_rate=[1,5,10]):
        """refresh_rate is a list of times [s] at which to update the frame"""
        self.refresh_rate = refresh_rate
        self.size = len(refresh_rate)
        self.last_refresh = [time()] * self.size
        self.frame_buffer = [frame for i in range(self.size)]
        self.last_movement = time()

    def update_buffer(self, frame, i, is_motion):
        actual_time = time()
        if(is_motion):
                self.last_movement = actual_time
        
        if actual_time - self.last_refresh[i] >= self.refresh_rate[i]:
            self.frame_buffer[i] = frame
            self.last_refresh[i] = actual_time

    def get_buffer(self):
        return self.frame_buffer
    
    def get_last_movement_time(self):
        return self.last_movement

    def get_size(self):
        return self.size

    def get_frame(self, index):
        return self.frame_buffer[index]