import os
import sys
from signal import signal, SIGINT
import cv2
import time
import pyzed.sl as sl

# ZED Camera declaration
zed = sl.Camera()

# Create a callback function for handling Ctrl-C
def handler(sig, frame):
	zed.disable_recording()
	zed.disable_streaming()
	zed.close()
	sys.exit(0)

# signal.signal is used to assign the handler function to SIGINT
signal(SIGINT, handler)


def main():	
	# The IP address of the sender must be set.
	if len(sys.argv) > 1:
		ip = sys.argv[1]
	else: 
		print('Please Provide an IP address.')
		exit(1)	
	
	# configuration parameters
	print("[INFO] SETTING INIT PARAMETERS")
	init_params = sl.InitParameters()
	init_params.camera_resolution = sl.RESOLUTION.HD720
	init_params.camera_fps = 60
	# Choose depth_mode among NONE, PERFORMANCE, QUALITY, ULTRA
	init_params.depth_mode = sl.DEPTH_MODE.NONE 
	# Set the source of the video to a video stream
	init_params.set_from_stream(ip)
	
	print("[INFO] OPENING CAMERA")	
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print(repr(status))
		exit(1)
	
	print("[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters(enable_depth = False)
	
#	# Create an image object, Mat, then retrieve left image of each frame
# 	# and display it with OpenCV.
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

	# # We can also enable Recording if needed
	# rec_path = "/home/smarttap2/Documents/ZED/stream1.svo"
	# recording_param = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H264)
	# err = zed.enable_recording(recording_param)
	# if err != sl.ERROR_CODE.SUCCESS:
	# 	print(repr(err))
	# 	exit(1)
	# print("SVO is Recording, use Ctrl-C to stop.")

	# Frame aquistion
	while True:
		if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS :
			# printing the difference between time when the frame was captured
			# ... and the time when the frame was received
			print(zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_milliseconds()-zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds())


if __name__=="__main__":
	main()
	
	
