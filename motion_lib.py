from imutils.video import VideoStream
from motion_buffer_lib import MotionBuffer
import argparse
import datetime
import imutils
import time
import cv2
from record_lib import Recorder

WIDTH = 300
HEIGHT = -1 #not used rn -1 should preserve the frame ratio i guess

DEF_ARGS={'blur_x':25, 'blur_y':25, 'treshold':40, 'min_area':4000,
	      'ref_reset':10}	#if ref_reset is None its never updated

class MotionTracker():
	def __init__(self, args=DEF_ARGS.copy()):
		self.params = args
		self.cap = None
		self.frame_time = None
		self.video_source = None # to remember what we are streaming
		self.ref_frame_age = 0
		self.motion_buffer = None
		self.cap_size = None	#(width, height) of currently captured video
		self.recorder = Recorder(5)

	def set_params(self, args):
		self.params = args

	def get_params(self):
		return self.params

	def start_capture(self, video_source=0):
		if self.is_capturing():
			print("Can't start another capture while capturing.")
			return 
		self.video_source = video_source
		self.cap = cv2.VideoCapture(video_source)
		if not self.cap.isOpened():
			self.cap.open()

	def read_frame(self):
		frame = self.cap.read()
		frame = frame if self.video_source is None else frame[1]
		if frame is None:
			self.stop_capture()
			return None
		return frame

	def parse_frame(self, frame):
		resized = imutils.resize(frame, width=WIDTH)
		#frame to grayscale
		gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
		#apply blur to mask the camera inaccuracies
		blur_radius_x = self.params.get('blur_x', DEF_ARGS['blur_x'])
		blur_radius_y = self.params.get('blur_y', DEF_ARGS['blur_y'])
		blurred = cv2.GaussianBlur(gray, (blur_radius_x, blur_radius_y), cv2.BORDER_DEFAULT)
		parsed = blurred
		if self.motion_buffer is None:
			self.motion_buffer = MotionBuffer(parsed)
		return parsed

	def calc_diff(self, grey_frame, ref_frame):
		# compute the absolute difference between the current frame and the first frame
		frame_delta = cv2.absdiff(ref_frame, grey_frame)
		return frame_delta
		

	def calc_bit(self, frame_delta):
		treshold = self.params.get('treshold', DEF_ARGS['treshold'])
		#if value lower than treshold, set it to 0, else to 255
		#[1] is getting the frame (i think, cant find ref)
		thresh = cv2.threshold(frame_delta, treshold, 255, cv2.THRESH_BINARY)[1] 
		# dilate the thresholded image to fill in holes
		thresh = cv2.dilate(thresh, None, iterations=1)
		return thresh

	def draw_contours(self, frame, bit, color):
		cnts = cv2.findContours(
			bit.copy(), #not modifying the bit image, to show it in the debug
			cv2.RETR_EXTERNAL, #all the countours with no real hierarchy
			cv2.CHAIN_APPROX_SIMPLE) #simplify the shape

		cnts = imutils.grab_contours(cnts)	#idk
		min_area = self.params.get('min_area', DEF_ARGS['min_area'])
		# loop over the contours
		found_movement = False
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < min_area:
				continue
			# compute the bounding box for the contour, draw it on the frame and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			scale = self.get_capture_shape()[0]/WIDTH
			x, y, w, h = int(x*scale), int(y*scale), int(w*scale), int(h*scale)
			found_movement = True
			# frame to draw on, top corner, bottom corner, color, thiccccknesss
			cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

		return found_movement

	def get_capture_shape(self):
		width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
		return (int(width), int(height))

	def get_capture_framerate(self):
		if self.is_capturing():
			return self.cap.get(cv2.CAP_PROP_FPS)
		else:
			return None

	def detect(self, parsed, draw_on):	#motion is same as is_motion
		motion = False
		contour_colors = [(0,50,255), (0,120,255), (0,255,255)]
		for i, ref in enumerate(reversed(self.motion_buffer.get_buffer())):
			delta = self.calc_diff(parsed, ref)
			bit = self.calc_bit(delta)
			is_motion = self.draw_contours(draw_on, bit, contour_colors[i])
			if is_motion:
				motion = True
			self.motion_buffer.update_buffer(parsed, i, is_motion) #TODO change i to ref or smth
		#sorry im putting it here. It hurts me as much as it hurts You, maybe
		return delta, bit, motion

	def save_motion(self, frame, is_motion):
		if is_motion:
			if not self.recorder.is_recording():
				fps = self.get_capture_framerate()
				self.recorder.start(fps, *list(self.get_capture_shape())) #unpacking a tuple :c
			self.recorder.save_frame(frame)
		elif self.recorder.is_recording():
			#recorder waits a bit after last seen activity
			if time.time() - self.motion_buffer.get_last_movement_time() > self.recorder.wait_time:
				self.recorder.stop()

	def show_time(self, frame):
		cv2.putText(frame, 
			datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),	#data
			(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2) #format
	
	def stop_capture(self):
		#stop if video, release if camera i think
		if self.is_capturing:
			self.motion_buffer = None
			self.cap.release()
			self.video_source = None
			self.cap = None
			self.cap_size = None
			if self.recorder.is_recording():
				self.recorder.stop()
		else:
			print("Can't stop a non capturing capture")

	def is_capturing(self):
		return self.cap is not None
