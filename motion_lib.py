from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

WIDTH = 500
HEIGHT = -1  # not used rn -1 should preserve the frame ratio i guess


def parse_int(param_value):
	return int(param_value)


def parse_int_odd(param_value):
	return int(param_value)//2*2 + 1


class Parameter:
	def __init__(self, min_value=0, max_value=100, default=0, parse=parse_int):
		self.min_value = min_value
		self.max_value = max_value
		self.default = default
		self.parse = parse


PARAMETERS = {
	'blur_x': Parameter(0, 50, default=25, parse=parse_int_odd),
	'blur_y': Parameter(0, 50, default=25, parse=parse_int_odd),
	'threshold': Parameter(0, 100, default=40),
	'min_area': Parameter(0, 8000, default=4000),
	'ref_reset': Parameter(0, 20, default=10)
}  # if ref_reset is None its never updated


class MotionTracker:
	def __init__(self, params=None):
		if params is None:
			params = {}

		self.params = params
		self.cap = None
		self.ref_frame = None
		self.video_source = None # to remember what we are streaming
		self.ref_frame_age = 0

	def set_params(self, args):
		self.params = args

	def get_params(self):
		return self.params

	def _get_param_value(self, key):
		return self.params.get(key, PARAMETERS[key].default)

	def start_capture(self, video_source=None):
		if self.is_capturing():
			print("Can't start another capture while capturing.")
			return 
		if video_source is None:
			# read from the webcam
			self.cap = VideoStream(src=0).start()
			# time.sleep(1.0) #let the camera warm up
		else:
			# otherwise, read from the video file
			self.video_source = video_source
			self.cap = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)

	def read_frame(self):
		frame = self.cap.read()
		frame = frame if self.video_source is None else frame[1]
		if frame is None:
			self.stop_capture()
			return None
		return frame

	def update_ref_frame(self, parsed):
		max_age = self._get_param_value('ref_reset')
		# the ref frame has not been initialized or its time to change it
		if self.ref_frame is None or self.ref_frame_age == max_age:
			self.ref_frame = parsed
			self.ref_frame_age = 0
		self.ref_frame_age += 1

	def parse_frame(self, frame):
		resized = imutils.resize(frame, width=WIDTH)
		# frame to grayscale
		gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
		# apply blur to mask the camera inaccuracies
		blur_radius_x = self._get_param_value('blur_x')
		blur_radius_y = self._get_param_value('blur_y')
		blurred = cv2.GaussianBlur(gray, (blur_radius_x, blur_radius_y), cv2.BORDER_DEFAULT)
		parsed = blurred
		self.update_ref_frame(parsed)
		return parsed

	def calc_diff(self, grey_frame):
		# compute the absolute difference between the current frame and the first frame
		assert self.ref_frame is not None
		frame_delta = cv2.absdiff(self.ref_frame, grey_frame)
		return frame_delta
		

	def calc_bit(self, frame_delta):
		threshold = self._get_param_value('threshold')
		# if value lower than threshold, set it to 0, else to 255
		# [1] is getting the frame (i think, cant find ref)
		thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
		# dilate the thresholded image to fill in holes
		thresh = cv2.dilate(thresh, None, iterations=2)
		return thresh

	def show_contours(self, frame, gray, thresh):
		cnts = cv2.findContours(
			thresh.copy(),  # not modifying the tresh image, to show it in the debug
			cv2.RETR_EXTERNAL,  # all the countours with no real hierarchy
			cv2.CHAIN_APPROX_SIMPLE)  # simplify the shape

		cnts = imutils.grab_contours(cnts)	#idk
		min_area = self._get_param_value('min_area')
		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < min_area:
				continue
			# compute the bounding box for the contour, draw it on the frame and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			# frame to draw on, top corner, bottom corner, color, thiccccknesss
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

	def show_time(self, frame):
		cv2.putText(frame, 
			datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),	#data
			(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1) #format
	
	def stop_capture(self):
		# stop if video, release if camera i think
		if self.is_capturing:
			self.cap.stop()
			self.cap = None
		else:
			print("Can't stop a non capturing capture")

	def is_capturing(self):
		return self.cap is not None
