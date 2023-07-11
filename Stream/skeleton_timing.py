# This is a modeified version of a group of scripts provided in the ZED documentation.

# Imports
import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import time



# Specify SVO path parameter
print("Specify SVO path parameter\n".upper())
svo_input_path = r'D:\Smart-Tap\DC kau processed\cut_svo\Middle\dc-kau-d1-t4_cut.svo'
init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                        svo_real_time_mode=False,
                        coordinate_units = sl.UNIT.MILLIMETER,
                        coordinate_system = sl.COORDINATE_SYSTEM.IMAGE,
                        depth_mode=sl.DEPTH_MODE.ULTRA) # Choose among NEURAL, ULTRA, QUALITY, PERFORMANCE
init_params.set_from_svo_file(str(svo_input_path))

# Create ZED objects
print("Create ZED objects".upper())
zed = sl.Camera()

# Open the SVO file specified
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    sys.stdout.write(repr(err))
    zed.close()
    exit()
print(zed.get_camera_information().camera_fps)

# Enable Positional tracking (mandatory for object detection)
positional_tracking_parameters = sl.PositionalTrackingParameters()
positional_tracking_parameters.set_as_static = True
zed.enable_positional_tracking(positional_tracking_parameters)
obj_param = sl.ObjectDetectionParameters()      # Define the Object Detection module parameters
obj_param.enable_body_fitting = False           # Smooth skeleton move
obj_param.enable_tracking = True                # Track people across images flow
obj_param.image_sync = True                     # run detection for every Camera grab
# choose among HUMAN_BODY_ACCURAT, HUMAN_BODY_MEDIUM, HUMAN_BODY_FAST
obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_ACCURATE  
obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use
obj_param.prediction_timeout_s = 0.2            # Defalt. The time taken before change from present to searching

print("Object Detection: Loading Module...")
err = zed.enable_object_detection(obj_param)
if err != sl.ERROR_CODE.SUCCESS:
    print(repr(err))
    zed.close()
    exit(1)

# runtime parameters
rt_param = sl.RuntimeParameters(enable_depth=True)
obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
obj_runtime_param.detection_confidence_threshold = 40

# Prepare single image containers
left_image = sl.Mat()
# Create ZED objects filled in the main loop
bodies = sl.Objects()

nb_frames = zed.get_svo_number_of_frames()

durations = []
kp = []
while True:
    if zed.grab(rt_param) == sl.ERROR_CODE.SUCCESS:
        svo_position = zed.get_svo_position()

        
        st = time.time()
        # Retrieve SVO images
        zed.retrieve_image(left_image, sl.VIEW.LEFT)
        # Retrieve objects
        zed.retrieve_objects(bodies, obj_runtime_param)
        # Extract skeleton data of each person
        for obj in bodies.object_list:            
            # print(obj.keypoint) # Update the keypoints list of the current person
            kp.append(obj.keypoint)
        e = time.time()

        durations.append(e-st)

        # Check if we have reached the end of the video
        if svo_position >= 1200:  # End of SVO
            sys.stdout.write("\nExiting now.\n")
            break

print("Skeleton Average Extract Duration: ", np.mean(durations))
print("Skeleton Max Extract Duration: ", np.max(durations))
print("Skeleton Min Extract Duration: ", np.min(durations))

zed.close()
