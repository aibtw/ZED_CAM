import os
import sys
from signal import signal, SIGINT
import cv2
import time
import pyzed.sl as sl

# ========== Global Variables ========== # 
zeds = []  # Holder for Cameras	

# ========== Ctrl-C Handler ========== #

def handler(sig, frame):
	global zeds
	
	for zed in zeds:
		zed.disable_recording()
		zed.close()
	sys.exit(0)

signal(SIGINT, handler)

def main():	
	global zeds
	
	print("[INFO] SETTING PATH")
	rec_path = "/home/felemban/Documents/ZED/test.svo"
#	rec_path = "/media/felemban/Extreme SSD/rec3.svo"
	print("[INFO] SETTING INIT PARAMETERS")
	# configuration parameters
	init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
					camera_fps=60,
					depth_mode=sl.DEPTH_MODE.NONE)
#	init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
		
	# Obtain available devices' serial numbers
	available_devices = sl.Camera.get_device_list()	
	
	serials = [] 	# Serial number of each camera
	for i, dev in enumerate(available_devices): 
		serials.append(dev.serial_number)
		init_params.set_from_serial_number(serials[i])
		zeds.append(sl.Camera())
		
		print("[INFO] OPENING CAMERA")	
		status = zeds[i].open(init_params)
		if status != sl.ERROR_CODE.SUCCESS:
			print(status)
			exit(1)
		
		print("[INFO] SETTING REC PARAMETERS")
		rec_params = sl.RecordingParameters(rec_path,
						    sl.SVO_COMPRESSION_MODE.H265)
		print("[INFO] ENABLING RECORDING")
		err = zeds[i].enable_recording(rec_params)
		if err != sl.ERROR_CODE.SUCCESS:
			print(repr(err))
			exit(1)
		
	runtime_params = sl.RuntimeParameters(enable_depth=False)
	frames = 0

	while True:
		for i in range(len(zeds)):
			if zeds[i].grab(runtime_params) == sl.ERROR_CODE.SUCCESS: 	# If success: image is available
				frames+=1
			print("Frame count: " + str(frames), end="\r")


if __name__=="__main__":
	main()
	
	
