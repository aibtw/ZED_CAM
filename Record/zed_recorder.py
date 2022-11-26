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


# # ========== Output Thread ========== #
# def csv_write_thread():
# 	print(f"[CSV-THREAD] STARTING ...")	
# 	global out_dict
# 	global stop_signal
	
# 	while not stop_signal:
# 		time.sleep(30)
# 		with open(rec_path.replace('svo', 'csv'), 'w') as csvfile:
# 			writer = csv.DictWriter(csvfile, fieldnames = ['id', 'ts', 'dropped'])
# 			writer.writeheader()
# 			writer.writerows(out_dict)
	
# 	print(f"[CSV-THREAD] EXIT ...")
# # Initialize the thread
# th = threading.Thread(target=csv_write_thread, args=())


# ========== Ctrl-C Handler ========== #
def handler(sig, frame):
	print("\n\nRecieved Ctrl-C signal!\n")
	global zed
	global stop_signal
	global th
	
	# print("[HANDLER] WAITING THREAD TO JOIN")
	# stop_signal = True
	# th.join()
	
	# Close ZED
	zed.disable_recording()
	zed.close()
	
	# Write output csv file
	with open(rec_path.replace('svo', 'csv'), 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = ['id', 'ts', 'dropped'])
		writer.writeheader()
		writer.writerows(out_dict)
	sys.exit(0)

# ========== Helping Functions ========== #
def path_check():
	global rec_path
	# Check if the user provided name with .svo or not. Added if not.
	if len(rec_path.split('.')) < 2: rec_path = rec_path.strip() + ".svo"
	# Check if the path already exists. Add a postfix to it if so.		
	if os.path.exists(rec_path):
		print("[ERROR] There already exists an experiment with this name! Enter another experiment name.")
		exit(1)
	return rec_path


def main():
	global zed
	global rec_path
	# global th
	
	# arg-parse and output path setting
	print("\n[INFO] SETTING PATH")
	if len(sys.argv) > 1: 
		rec_path = sys.argv[1]
		rec_path = path_check()
	else:
		print('[ERROR] Please Provide experiment path and name (e.g. Home/Desktop/exp1.svo))')
		exit(1)	
	
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
	
	# Starting thread
	# th.start()

	frames = -1
	dropped_frames = 0	

	# Start main loop
	while True:
		if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
			# Record timestamp
			ts = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()

			# Increament frames
			frames+=1
			
			# Record if there was dropped frames before this one and how many are dropped
			dropped = zed.get_frame_dropped_count()-dropped_frames
			dropped_frames+=dropped
			
			# Update output dictionary
			out_dict.append({'id': frames, 'ts': ts, 'dropped': dropped})
			
			# Show output on terminal
			#print(f"Frame: {frames}\tTime Stamp: {ts}\tDropped: {dropped}", end="\r")


if __name__=="__main__":
	main()


