#!/usr/bin/python3
import os
import sys
from signal import signal, SIGINT
import time
import threading
import csv
import pyzed.sl as sl


# ========== Global Variables ========== # 
zed = sl.Camera()  # Holder for Cameras	
out_dict = []
rec_path = ""
stop_signal = False

# ========== Ctrl-C Handler ========== #
def handler(sig, frame):
	print("\n\nRecieved Ctrl-C signal!\n")
	global zed
	global stop_signal
	global th
	
	# Close ZED
	zed.disable_recording()
	zed.close()
	
	sys.exit(0)

# ========== Helping Functions ========== #
def path_check():
	global rec_path
	# Check if the user provided name with .svo or not. Added if not.
	if len(rec_path.split('.')) < 2: rec_path = rec_path.strip() + ".svo"
	# Check if the path already exists. Add a postfix to it if so.		
	if os.path.exists(rec_path):
		inp = input("[WARNING] There already exists an experiment with this name! Do you wish to replace it? [Y/N]:  ")
		if inp == 'Y' or inp == 'y': return rec_path
		else: exit(1)
	return rec_path


def main():
	global zed
	global rec_path

	# arg-parse and output path setting
	print("\n[INFO] SETTING PATH")
	if len(sys.argv) > 1:
		rec_name = sys.argv[1]
		if len(rec_name.split("/")) > 1: # User has provided a path 
			if os.path.isdir(rec_name.split("/")[:-1]): # Check if user provided path is correct
				rec_path = rec_name
			else:
				print('[ERROR] The provided directory does not exist!')
		else: # only experiment name provided. No path. Use default path 
			rec_path = os.path.join('/home/felemban/Documents', rec_name)
		
		rec_path = path_check()
	else:
		print('[ERROR] Please Provide experiment name (e.g. exp1.svo))')
		exit(1)	
	
	print("\n[INFO] OUTPUT PATH SET TO: ", rec_path)
	
	# init signal handler
	signal(SIGINT, handler)
	
	print("\n[INFO] SETTING INIT PARAMETERS")
	init_params = sl.InitParameters(
			camera_resolution=sl.RESOLUTION.HD720,
			camera_fps=60,
			depth_mode=sl.DEPTH_MODE.NONE)
	
	print("\n[INFO] OPENING CAMERA")	
	status = zed.open(init_params)
	if status != sl.ERROR_CODE.SUCCESS:
		print(status)
		exit(1)
	
	print("\n[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters(enable_depth=False)

	print("\n[INFO] SETTING RECORDING PARAMETERS")
	rec_params = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H265)
	
	print("\n[INFO] ENABLING RECORDING")
	err = zed.enable_recording(rec_params)
	if err != sl.ERROR_CODE.SUCCESS:
		print(repr(err))
		exit(1)
	
	frames = -1
	dropped_frames = 0	

	# Start main loop
	while True:
		if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
			# Record timestamp
			ts = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()

			# Increament frames
#			frames+=1
			
			# Record if there was dropped frames before this one and how many are dropped
#			dropped = zed.get_frame_dropped_count()-dropped_frames
#			dropped_frames+=dropped
			
			# Update output dictionary
#			out_dict.append({'id': frames, 'ts': ts, 'dropped': dropped})
			
			# Show output on terminal
			#print(f"Frame: {frames}\tTime Stamp: {ts}\tDropped: {dropped}", end="\r")


if __name__=="__main__":
	main()


