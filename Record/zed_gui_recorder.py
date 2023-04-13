#!/usr/bin/python3
import os
import sys
from signal import signal, SIGINT
import time
from datetime import datetime
import threading
import csv
import pyzed.sl as sl
import tkinter as tk
from tkinter import messagebox


# ========== Global Variables ========== # 
zed = sl.Camera()  # Holder for Cameras	
is_recording = False


# ========== Ctrl-C Handler ========== #
def handler(sig, stack_frame):
	print("\n\nReceived Exit Signal!\n")
	global zed
	global is_recording

	# Close ZED
	is_recording=False
	time.sleep(0.5)
	zed.disable_recording()
	zed.close()
	
	sys.exit(0)


def on_close():
	ans = messagebox.askyesno("Close", message="Are you sure you wish to exit?")
	if ans:
		handler(None, None)


# ========== Recording Function ========== #
def rec_loop(status, runtime_params, rec_path):
	global zed
	global is_recording

	# Recording Parameters
	print("\n[INFO] SETTING RECORDING PARAMETERS")
	dt=datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
	rec_path = os.path.join(rec_path, dt+'.svo')
	print("[INFO] RECORDING TO: ", rec_path)
	rec_params = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H265)
	
	# Enable Recording
	print("\n[INFO] ENABLING RECORDING")
	err = zed.enable_recording(rec_params)
	if err != sl.ERROR_CODE.SUCCESS:
		print(repr(err))
		exit(1)
	
	# Start main loop
	status.set("Recording Started")
	while is_recording:
		zed.grab(runtime_params)


def main():
	global zed
	global is_recording

	# arg-parse and output path setting
	print("\n[INFO] SETTING PATH")
	if len(sys.argv) > 1:
		rec_path = sys.argv[1]
		if not os.path.exists(rec_path):
			os.mkdir(rec_path)
	print("\n[INFO] OUTPUT PATH SET TO: ", rec_path)
	
	# init signal handler
	signal(SIGINT, handler)
	
	# Init Parameters
	print("\n[INFO] SETTING INIT PARAMETERS")
	init_params = sl.InitParameters(
			camera_resolution=sl.RESOLUTION.HD720,
			camera_fps=60,
			depth_mode=sl.DEPTH_MODE.NONE)
	
	# Open the camera
	print("\n[INFO] OPENING CAMERA")	
	st = zed.open(init_params)
	if st != sl.ERROR_CODE.SUCCESS:
		print(st)
		exit(1)
	
	# Runtime Parameter
	print("\n[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters(enable_depth=False)

	# TK GUI Section
	root = tk.Tk()
	status = tk.StringVar()
	status.set("Recording Stopped")

	th=None  # Thread object holder

	# Action item for start recording button
	def start_recording():
		global is_recording
		if is_recording:
			print("Recordings Locked!")
			return
		is_recording = True

		th=threading.Thread(target=rec_loop, args=(status,runtime_params,rec_path,))
		th.start()
		
	# Action item for stop recording button
	def stop_recording():
		global is_recording
		if is_recording == False:
			print("Recording already stopped")
			return
		is_recording = False
		status.set("Recording Stopped")
		try:
			th.join()
		except:
			return
	
	frame = tk.Frame(master=root, width = 200, height=200)
	frame.pack(fill=tk.X, expand=False, side=tk.TOP)
	start_btn = tk.Button(master=frame, text="Start Recording", command=start_recording)
	start_btn.grid(row=1, column=1)
	stop_btn = tk.Button(master=frame, text="Stop Recording", command=stop_recording)
	stop_btn.grid(row=1, column=2)
	status_lbl = tk.Label(master=frame, textvariable=status)
	status_lbl.grid(row=2, column=1)
	root.protocol("WM_DELETE_WINDOW", on_close)
	root.mainloop()


	
if __name__=="__main__":
	main()


