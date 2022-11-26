import sys
import pyzed.sl as sl
import cv2
import time
import threading
import signal
import os

zeds = []
frames_recorded = 0
stop_signal = False
thread_list = []

def signal_handler(sig, frame):
	global stop_signal
	global zeds
	print("[SIG HANDLER] RECEIVED INTERRUPT")
	
	stop_signal = True
	for th in thread_list:
		th.join()
	
	for i in range(len(zeds)):
		zeds[i].disable_recording()
		zeds[i].close()
	sys.exit(0)


def get_frame(index, runtime_params):
	print(f"[THREAD {index}] STARTING ...")
	global stop_signal
	global zeds
	global frames_recorded	
	
	while not stop_signal:
		if zeds[index].grab(runtime_params) == sl.ERROR_CODE.SUCCESS :
			frames_recorded[index] += 1
		
	print(f"[THREAD {index}] EXIT ...")


def main():
	global zeds
	global thread_list
	global frames_recorded
	signal.signal(signal.SIGINT, signal_handler)
	
	if len(sys.argv) > 1:
		out_name = sys.argv[1]
	else: 
		print('Please Provide experiment name)')
		exit(1)	
	
	print("[INFO] SETTING INIT PARAMETERS\n")
	# configuration parameters
	init_params = sl.InitParameters(camera_resolution = sl.RESOLUTION.HD720,
					camera_fps = 30,
					depth_mode = sl.DEPTH_MODE.NONE) #sl.DEPTH_MODE.PERFORMANCE)
	
	print("[INFO] SETTING RUNTIME PARAMETERS\n")
	runtime_params = sl.RuntimeParameters(enable_depth=False)
	
	print("[INFO] CONNECTED/STREAMING DEVICES ARE: ")
	available_devices = {}
	for i, dev in enumerate(sl.Camera.get_streaming_device_list()):
		available_devices[f'ip {i}'] = dev.ip
	for i, dev in enumerate(sl.Camera.get_device_list()):
		available_devices[f'sn {i}'] = dev.serial_number
	print(available_devices)
	
	# Open each device and enable recording.
	for i, (key, value) in enumerate(available_devices.items()):
		print(f"\n[INFO] SETTING UP RECORDING ON CAMERA {i}")
		rec_path = f"/home/felemban/Documents/ZED/{out_name}_{i}.svo"
		recording_param = sl.RecordingParameters(rec_path, sl.SVO_COMPRESSION_MODE.H264, transcode_streaming_input=True)		

		if key.split(' ')[0] == 'ip':
			init_params.set_from_stream(value)
#			recording_param.transcode_streaming_input=True
		elif key.split(' ')[0] == 'sn':
			init_params.set_from_serial_number(value)
		
		print(f"[INFO] OPENING {value} CAMERA")	
		zeds.append(sl.Camera())
		status = zeds[i].open(init_params)
		if status != sl.ERROR_CODE.SUCCESS:
			print(repr(status))
			exit(1)
			
		print(f"[INFO] ENABLE RECORDING ON {value} CAMERA\n")
		err = zeds[i].enable_recording(recording_param)
		if err != sl.ERROR_CODE.SUCCESS:
			print(repr(err))
			exit(1)
		
	print("[INFO] Success! Press Ctrl+C to stop recording.\n\n")
	frames_recorded=[]
	for i in range(len(zeds)):
		frames_recorded.append(0)
		thread_list.append(threading.Thread(target=get_frame, args=(i, runtime_params, ))) # Note: Must have a (,) when passing args to thread
		thread_list[i].start()
	
	while True:
		print("Frame count: " + str(sum(frames_recorded)), end="\r")
		time.sleep(0.1)
		
	

if __name__=="__main__":
	main()
	
	
