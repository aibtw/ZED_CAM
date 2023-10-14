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
zed = sl.Camera()  		# Camera object	
is_recording = False	# Recording condition (Set false to stop any thread recording)
aborted = False			# Recording abortion indicator
n_frames = 0			# Tracks number of recorded frames in real-time

# =========== Ctrl-C Handler =========== #
def handler(sig, stack_frame):
	"""
		This function handles the Ctrl-C signal when received.

		Also, this function is called when close button is
		used, from within the on_close() function.
	"""

	print("\n\nReceived Exit Signal!\n")
	global zed					# Camera object
	global is_recording			# Recording condition (Set false to stop any thread recording)
	is_recording=False  		# Stop any threads that are recording
	time.sleep(0.5)				# Wait for the thread. (no need for a thread.join())
	zed.disable_recording()		# Disable recording
	zed.close()					# Close the camera
	sys.exit(0)					# Exit


# ======== Close-Button Handler ======== #
def on_close():
	"""
		This function handles the the close button.

		It calls the handler() function which disables
		recording and exits.
	"""

	# Show a confirmation Yes/No message box
	ans = messagebox.askyesno("Close", message="Are you sure you wish to exit?")
	if ans:						# If closing is confirmed
		handler(None, None)  	# Use the same Ctrl-C handler, no need to rewrite the code


# ========= Recording Function ========= #
def rec_loop(status, runtime_params, rec_path, usrid, dt):
	"""
		This function manages video recording. 
		
		whenever called, it sets a new recording path,
		then update recording parameters, and enable
		recording. Finally recording is started.
		The function is intended to be used as a thread.

		Parameters
		----------
		status: tk.StringVar()
			variable to store recording status for GUI
		runtime_params: sl.RuntimeParameters
			runtime parameters of the ZED camera
		rec_path: str
			Recording directory. must exists.
		usrid: int
			user id provided from GUI to use in file name.
	"""

	global zed 			 # Camera object
	global is_recording  # Recording condition (Set false to stop any thread recording)
	global aborted  	 # Recording abortion indicator
	global n_frames

	print("\n[INFO] SETTING RECORDING PARAMETERS")
	# Recording path
	rec_path = os.path.join(rec_path, dt+'.svo')  
	print("[INFO] RECORDING TO: ", rec_path) 
	# Recording Parameters
	rec_params = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H265)
	
	# Enable Recording
	print("\n[REC] ENABLING RECORDING")
	err = zed.enable_recording(rec_params)
	if err != sl.ERROR_CODE.SUCCESS:
		print(repr(err))
		exit(1)

	# Start main loop
	status.set("Recording Started")
	while is_recording:
		zed.grab(runtime_params)
		# Increment frame number only if it was written to svo.
		if zed.get_recording_status().status: n_frames += 1 
		
	# When the user asks to stop recording
	if aborted: 
		# If aborted, delete the file
		os.remove(rec_path)
		print("[REC] Recording Aborted and file was deleted")
	else:
		print("[REC] Recording Stopped")

	# Either way, disable recording and print number of dropped frames
	zed.disable_recording()
	print("[INFO] DROPPED FRAMES: ", zed.get_frame_dropped_count())
	

def main():
	global zed  		 # Camera object
	global is_recording  # Recording condition (Set false to stop any thread recording)
	global aborted  	 # Recording abortion indicator
	global n_frames

	# ========================= setup Section ========================= #
	# Set default rec_path
	# rec_path = r"/home/felemban/Documents"
	rec_path = r"/media/smarttap2/Extreme SSD/Smart-Tap Data KAUST"
	# rec_path = r"C:\Users\English\Documents\ZED"

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
	
	# Runtime Parameter
	print("\n[INFO] SETTING RUNTIME PARAMETERS")
	runtime_params = sl.RuntimeParameters(enable_depth=False)

	# Metadata structure initialization
	metadata_fname = ''
	metadata = [{"ID": [], "Position": [], "StartFrame": [],"EndFrame": [], "Marked": []},
	      		{"ID": [], "Position": [], "StartFrame": [],"EndFrame": [], "Marked": []}]
	
	
	# ========================= TK GUI Section ========================= #
	root = tk.Tk()
	status = tk.StringVar()			 # Store the status of recording
	status.set("Recording Stopped")	 # Initially set to stopped
	usrid=tk.IntVar()				 # Store the user ID
	usrid.set(-1)					 # Initially set to -1
	fps=tk.IntVar()					 # Store current FPS
	fps.set(0)						 # initially set to 0
	
	# The same button is used for start/stop. So, to iterate the text,
	# ... the test is initialized as tk.StringVar() which changes in rt.
	usr_btn_stat = [tk.StringVar(), tk.StringVar()]  		# Start/Stop buttons' texts holder
	[btn_stat.set('Start') for btn_stat in usr_btn_stat]	# Initialized to Start

	active_usrs = tk.IntVar()	# Store number of active users (0, 1, 2)
	active_usrs.set(0)			# Initialize to 0

	mark=[False, False]
	th=None  			# Thread object holder
	recstat_lbl=None	# Recording status label object holder. 
						# Initialized here to avoid (variable mentioned
						# before initializing) errors when excuting
						# the start_recording function


	# Action item for start recording
	def start_recording():
		global zed
		global is_recording
		nonlocal metadata
		nonlocal metadata_fname

		# If recording is already started (there is already an active user using the interface)
		# ... then no need to start the recording again, as it is already running.
		if is_recording:
			print("Recordings Locked!")
			# Returning true indicates that the recording is running
			return True
		# If the camera is not open, then open it.
		if not zed.is_opened():
			print("Opening camera")
			st = zed.open(init_params)
			if st != sl.ERROR_CODE.SUCCESS:
				print(st)
				return False
		# Set recording flag to True
		is_recording = True
		# Update status label color
		recstat_lbl.configure(bg="#25be46")
		# Current date & time
		dt=datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
		# Start the recording thread
		th=threading.Thread(target=rec_loop, args=(status,runtime_params,rec_path,usrid,dt))
		th.start()
		# Set the file name of the output file to the time at which the recording started at
		metadata_fname = dt
		# Returning true indicates that the recording is running
		return True


	# Action item for stop recording button
	def stop_recording():
		global zed
		global is_recording
		global n_frames
		
		# If recording is already stopped
		if is_recording == False:
			print("Recording already stopped")
			messagebox.showerror("Error", "Recording already stopped!")
			return
		
		# Check if there is still a user using the interface
		if active_usrs.get() != 0:
			print("A user is still engaged. Waiting for them.")
			# return datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
			_n_frames = n_frames
			return _n_frames
		
		# Reset the recording flag
		is_recording = False
		# Update the recording status label  
		status.set("Recording Stopped")
		# Wait for the thread
		try:
			th.join()
		except:
			# Update status label
			recstat_lbl.configure(bg="#de5e5e")  
			# Close the camera
			zed.close()
			# return datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
			_n_frames = n_frames
			n_frames = 0
			return _n_frames


	# Read User id input
	def usr_action(id_ent, usr, pressed_mark=False):
		global zed
		nonlocal metadata
		nonlocal metadata_fname
		nonlocal mark
		
		# Get the ID of the current user
		ID = id_ent.get()
		# Check if an ID is provided and if is integer
		try:
			usrid.set(int(ID))
			if usrid.get() < 0: raise ValueError
		except ValueError:
			print("Please provide correct user id")
			messagebox.showerror("Error", "Please provide correct user id")
			return
		
		# If trying to report a recording without starting to record
		if pressed_mark and usr_btn_stat[usr].get() == "Start":
			print("Can't mark low quality when recording not started")
			return

		# If the user pressed start
		if usr_btn_stat[usr].get() == "Start":
			# Update the button text to stop (and its functionality changes with it)
			usr_btn_stat[usr].set("Stop")
			# Check if camera opened successfully
			if start_recording() == False: 
				messagebox.showerror("ERROR", "Camera Failed To Open")
				return
			# Set StartFrame for this user in metadata
			# If this is the a new recording:
			if active_usrs.get() == 0:
				# Then starting time is same as recording start time
				# metadata[usr]["StartFrame"].append(metadata_fname)
				metadata[usr]["StartFrame"].append(0)
			# If not new recording (previous user started recording and current user joined later):
			else: 
				# Then start time is now.
				# metadata[usr]["StartFrame"].append(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
				metadata[usr]["StartFrame"].append(n_frames)
			# Set other parts of metadata
			metadata[usr]["ID"].append(usrid.get())
			metadata[usr]["Position"].append(usr)
			# Increment number of active users.
			active_usrs.set(active_usrs.get() + 1)
		
		# If the user pressed stop
		elif usr_btn_stat[usr].get() == "Stop":
			# Check for pressing the mark and report button
			if pressed_mark: mark[usr] = not mark[usr]
			# Update the button text to start (and its functionality changes with it)
			usr_btn_stat[usr].set("Start")
			# Decrement active users
			active_usrs.set(active_usrs.get() - 1)
			# update metadata
			# metadata[usr]["EndFrame"].append(stop_recording())
			metadata[usr]["EndFrame"].append(stop_recording())
			metadata[usr]["Marked"].append(mark[usr])
			# Reset the mark of this position for the next user
			mark[usr] = False
			# Reset the ID of the person
			id_ent.delete(0, tk.END)
			# Write the metacata file only if there are no active users
			if active_usrs.get() == 0:  
				# Preparing and writing metadata output
				output_dict = {}
				# The metadata dictionary has two lists, one for each user position
				# Each position can contain more than one datapoint (more than one user)
				# Merge the two lists into one dictionary
				for k in metadata[0].keys():
					output_dict[k] = metadata[0][k] + metadata[1][k]
				# Write metadata to a csv file
				with open(os.path.join(rec_path, metadata_fname)+'.csv', 'w', newline='') as output_file:
					writer = csv.writer(output_file)
					writer.writerow(list(output_dict.keys()))
					writer.writerows(zip(*output_dict.values()))

				# Reset metadata for next recording
				metadata = [{"ID": [], "Position": [], "StartFrame": [],"EndFrame": [], "Marked": []},
							{"ID": [], "Position": [], "StartFrame": [],"EndFrame": [], "Marked": []}]
				metadata_fname = ''


	# Creating Main Frame
	frm_main = tk.Frame(master=root, width = 500, height=500)
	frm_main.pack(fill=tk.X, expand=False, side=tk.TOP)
	# Configuring number of rows and columns in the grid
	frm_main.columnconfigure([i for i in range(5)], weight=1, minsize=75)
	frm_main.rowconfigure([i for i in range(10)], weight=1, minsize=75)
	# Label that reads (Enter your number) for each of the two users
	id_lbl = tk.Label(master=frm_main, text="Enter your phone number", font=('Times New Roman', 14), bg="#A6DDFD")
	id_lbl.grid(row=3, column=0, padx=(15,0), pady=(15,15), sticky="E")
	id_lbl = tk.Label(master=frm_main, text="Enter your phone number", font=('Times New Roman', 14), bg="#B9FFBB")
	id_lbl.grid(row=4, column=0, padx=(15,0), pady=(15,15), sticky="E")
	# Entry that receives the ID or number from each of the two users
	id_ent_0 = tk.Entry(master=frm_main, font=('Times New Roman', 14), bg="#A6DDFD")
	id_ent_0.grid(row=3, column=1, columnspan=1, padx=(15,0), pady=(15,15), sticky="EW")
	id_ent_1 = tk.Entry(master=frm_main, font=('Times New Roman', 14), bg="#B9FFBB")
	id_ent_1.grid(row=4, column=1, columnspan=1, padx=(15,0), pady=(15,15), sticky="EW")
	# Button for confirming the entered ID or number for each of the two users
	st_btn_0 = tk.Button(master=frm_main, textvariable=usr_btn_stat[0], command=lambda: usr_action(id_ent_0, 0), font=('Times New Roman', 14))
	st_btn_0.grid(row=3, column=2, padx=(15,15), pady=(15,15), sticky="EW")
	st_btn_1 = tk.Button(master=frm_main, textvariable=usr_btn_stat[1], command=lambda: usr_action(id_ent_1, 1), font=('Times New Roman', 14))
	st_btn_1.grid(row=4, column=2, padx=(15,15), pady=(15,15), sticky="EW")
	# Button for marking the recording as needs review
	m_btn_0 = tk.Button(master=frm_main, text="Stop & Report", command=lambda: usr_action(id_ent_0, 0, True), font=('Times New Roman', 14))
	m_btn_0.grid(row=3, column=3, padx=(15,15), pady=(15,15), sticky="EW")
	m_btn_1 = tk.Button(master=frm_main, text="Stop & Report", command=lambda: usr_action(id_ent_1, 1, True), font=('Times New Roman', 14))
	m_btn_1.grid(row=4, column=3, padx=(15,15), pady=(15,15), sticky="EW")
	# Show recording Status
	status_lbl = tk.Label(master=frm_main, text="Status", font=('Times New Roman', 14))
	status_lbl.grid(row=6, column=0, padx=(15,0), pady=(15,15), sticky="NSE")
	recstat_lbl = tk.Label(master=frm_main, textvariable=status, font=('Times New Roman', 14), bg="#de5e5e")
	recstat_lbl.grid(row=6, column=1, columnspan=3, padx=(15,15), pady=(15,15), sticky="NSW")

	# curid_lbl = tk.Label(master=frm_main, text="Current User: ", font=('Times New Roman', 14))
	# curid_lbl.grid(row=2, column=0, padx=(15,0), pady=(15,15), sticky="NSE")
	# conf_curid_lbl = tk.Label(master=frm_main, textvariable= usrid, font=('Times New Roman', 14))
	# conf_curid_lbl.grid(row=2, column=1, columnspan=3, padx=(15,15), pady=(15,15), sticky="NSW")
	# ctrl_lbl = tk.Label(master=frm_main, text="Controls: ", font=('Times New Roman', 14))
	# ctrl_lbl.grid(row=3, column=0, padx=(15,0), sticky="NSE")
	# start_btn = tk.Button(master=frm_main, text="Start Recording", font=('Times New Roman', 14), command=start_recording)
	# start_btn.grid(row=3, column=1, padx=(15,0), sticky='EW')
	# stop_btn = tk.Button(master=frm_main, text="Stop Recording", font=('Times New Roman', 14), command=stop_recording)
	# stop_btn.grid(row=3, column=2,padx=(0,0), sticky='EW')
	# abort_btn = tk.Button(master=frm_main, text="Abort Recording", font=('Times New Roman', 14), command=abort_recording)
	# abort_btn.grid(row=3, column=3,padx=(0,15), sticky='EW')

	
	# fps_lbl = tk.Label(master=frm_main, text="FPS: ", font=('Times New Roman', 14))
	# fps_lbl.grid(row=5, column=0, columnspan=4, padx=(15,15), pady=(15,15), sticky="NSEW")
	# curfps_lbl = tk.Label(master=frm_main, textvariable=fps, font=('Times New Roman', 14))
	# curfps_lbl.grid(row=5, column=0, columnspan=4, padx=(15,15), pady=(15,15), sticky="NSEW")

	root.protocol("WM_DELETE_WINDOW", on_close)
	root.mainloop()


if __name__=="__main__":
	main()


