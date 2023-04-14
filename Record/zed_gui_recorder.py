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
	global zed					# Camera object
	global is_recording			# Recording condition (Set false to stop any thread recording)
	is_recording=False  		# Stop any threads that are recording
	time.sleep(0.5)				# Wait for the thread. (this will suffice, No need for a thread.join())
	zed.disable_recording()		# Disable recording
	zed.close()					# Close the camera
	sys.exit(0)					# Exit


# ========== Close-Button Handler ========== #
def on_close():
	ans = messagebox.askyesno("Close", message="Are you sure you wish to exit?")
	if ans:						# If closing is confirmed
		handler(None, None)  	# Use the same Ctrl-C handler, no need to rewrite the code


# ========== Recording Function ========== #
def rec_loop(status, runtime_params, rec_path, usrid, fps):
	global zed
	global is_recording

	# Recording Parameters
	print("\n[INFO] SETTING RECORDING PARAMETERS")
	dt=datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
	rec_path = os.path.join(rec_path, str(usrid.get())+"_"+dt+'.svo')
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
		# fps.set(int(zed.get_current_fps()))


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
	usrid=tk.IntVar()
	usrid.set(-1)
	fps=tk.IntVar()
	fps.set(0)
	
	th=None  # Thread object holder
	recstat_lbl=None

	# Action item for start recording button
	def start_recording():
		global is_recording
		if is_recording:
			print("Recordings Locked!")
			return
		if usrid.get() < 0:
			print("Please provide correcut user id")
			return
		is_recording = True
		recstat_lbl.configure(bg="#25be46")  # Update status label color
		th=threading.Thread(target=rec_loop, args=(status,runtime_params,rec_path,usrid,fps))
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
			fps.set(0)
			recstat_lbl.configure(bg="#de5e5e")  # Update status label
			return

	# Read User id input
	def conf_id():
		inp = id_ent.get()
		try:
			usrid.set(int(inp))
		except ValueError:
			print("Please enter an integer")

	frm_main = tk.Frame(master=root, width = 500, height=500)
	frm_main.pack(fill=tk.X, expand=False, side=tk.TOP)
	frm_main.columnconfigure([i for i in range(4)], weight=1, minsize=75)
	frm_main.rowconfigure([i for i in range(10)], weight=1, minsize=75)
	
	id_lbl = tk.Label(master=frm_main, text="Enter your phone number", font=('Times New Roman', 14))
	id_lbl.grid(row=0, column=0, padx=(15,0), pady=(15,15), sticky="E")
	id_ent = tk.Entry(master=frm_main, font=('Times New Roman', 14))
	id_ent.grid(row=0, column=1, columnspan=2, padx=(15,0), pady=(15,15), sticky="EW")
	conf_btn = tk.Button(master=frm_main, text="Confirm", command=conf_id, font=('Times New Roman', 14))
	conf_btn.grid(row=0, column=3, padx=(15,15), pady=(15,15), sticky="W")
	
	curid_lbl = tk.Label(master=frm_main, text="Current User: ", font=('Times New Roman', 14))
	curid_lbl.grid(row=1, column=0, padx=(15,0), pady=(15,15), sticky="NSE")
	conf_curid_lbl = tk.Label(master=frm_main, textvariable= usrid, font=('Times New Roman', 14))
	conf_curid_lbl.grid(row=1, column=1, columnspan=3, padx=(15,15), pady=(15,15), sticky="NSW")

	ctrl_lbl = tk.Label(master=frm_main, text="Controls: ", font=('Times New Roman', 14))
	ctrl_lbl.grid(row=3, column=0, padx=(15,0), sticky="NSE")
	start_btn = tk.Button(master=frm_main, text="Start Recording", font=('Times New Roman', 14), command=start_recording)
	start_btn.grid(row=3, column=1, padx=(15,0), sticky='EW')
	stop_btn = tk.Button(master=frm_main, text="Stop Recording", font=('Times New Roman', 14), command=stop_recording)
	stop_btn.grid(row=3, column=2,padx=(0,15), sticky='EW')
	
	status_lbl = tk.Label(master=frm_main, text="Status", font=('Times New Roman', 14))
	status_lbl.grid(row=4, column=0, padx=(15,0), pady=(15,15), sticky="NSE")
	recstat_lbl = tk.Label(master=frm_main, textvariable=status, font=('Times New Roman', 14), bg="#de5e5e")
	recstat_lbl.grid(row=4, column=1, columnspan=3, padx=(15,15), pady=(15,15), sticky="NSW")
	
	# fps_lbl = tk.Label(master=frm_main, text="FPS: ", font=('Times New Roman', 14))
	# fps_lbl.grid(row=5, column=0, columnspan=4, padx=(15,15), pady=(15,15), sticky="NSEW")
	# curfps_lbl = tk.Label(master=frm_main, textvariable=fps, font=('Times New Roman', 14))
	# curfps_lbl.grid(row=5, column=0, columnspan=4, padx=(15,15), pady=(15,15), sticky="NSEW")

	root.protocol("WM_DELETE_WINDOW", on_close)
	root.mainloop()


	
if __name__=="__main__":
	main()


