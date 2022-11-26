import os
import sys
from signal import signal, SIGINT
import cv2
import time
import pyzed.sl as sl


zed = sl.Camera()

def handler(sig, frame):
	zed.disable_recording()
	zed.disable_streaming()
	zed.close()
	sys.exit(0)

signal(SIGINT, handler)

def main():	
	print("[INFO] SETTING INIT PARAMETERS")
	# configuration parameters
	init_params = sl.InitParameters()
	init_params.camera_resolution = sl.RESOLUTION.HD720
	init_params.camera_fps = 30
	init_params.depth_mode = sl.DEPTH_MODE.NONE
#	init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE

		
	print("[INFO] OPENING CAMERA")	
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print(repr(status))
		exit(1)
	
	print("[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters()

	print("[INFO] SETTING STREAMING PARAMETERS")
	stream_params = sl.StreamingParameters()
	stream_params.codec = sl.STREAMING_CODEC.H264
	stream_params.bitrate = 4000
	
	print("[INFO] ENABLE STREAMING")
	status = zed.enable_streaming(stream_params)
	
	if status != sl.ERROR_CODE.SUCCESS:
		print(repr(status))
		exit(1)
	
	print("Use Ctrl+C to exit\n")

	while True:
		err = zed.grab(runtime_params)

if __name__=="__main__":
	main()
	
	
