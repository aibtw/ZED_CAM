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
	if len(sys.argv) > 1:
		ip = sys.argv[1]
	else: 
		print('Please Provide an IP address.')
		exit(1)	
	
	print("[INFO] SETTING INIT PARAMETERS")
	# configuration parameters
	init_params = sl.InitParameters()
	init_params.camera_resolution = sl.RESOLUTION.HD720
	init_params.camera_fps = 30
#	init_params.depth_mode = sl.DEPTH_MODE.NONE
	init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
	
	init_params.set_from_stream(ip)
	
		
	print("[INFO] OPENING CAMERA")	
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print(repr(status))
		exit(1)
	
	print("[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters()
	
#	mat = sl.Mat()
#	
#	print("Use Q to exit, or Ctrl+C \n")
#	key = ''
#	while key != 113:
#		err = zed.grab(runtime_params)
#		if err == sl.ERROR_CODE.SUCCESS:
#			zed.retrieve_image(mat, sl.VIEW.LEFT)
#			cv2.imshow("ZED", mat.get_data())
#		key = cv2.waitKey(1)
#	cv2.destroyAllWindows()

	rec_path = "/home/felemban/Documents/ZED/str1.svo"

	recording_param = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H264)
	err = zed.enable_recording(recording_param)
	if err != sl.ERROR_CODE.SUCCESS:
		print(repr(err))
		exit(1)

	print("SVO is Recording, use Ctrl-C to stop.")
	frames_recorded = 0

	while True:
		if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS :
			frames_recorded += 1
			print("Frame count: " + str(frames_recorded), end="\r")

if __name__=="__main__":
	main()
	
	
