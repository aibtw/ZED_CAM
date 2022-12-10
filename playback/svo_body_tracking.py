import sys
import cv2
import numpy as np
from tkinter import *
import pyzed.sl as sl
from utils import *
import tracking_viewer

# Global
paused = False
cam = sl.Camera()


def main():
    print("\nSTARTING ...\n")

    global paused   # A flag for pausing the video
    global cam      # Variable to hold ZED object

    # Init parameters
    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                            svo_real_time_mode=True,
                            coordinate_units = sl.UNIT.MILLIMETER,
                            coordinate_system = sl.COORDINATE_SYSTEM.IMAGE,
                            depth_mode=sl.DEPTH_MODE.ULTRA)
    
        # Arg parse
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
        init.set_from_svo_file(filepath)
        print("Reading SVO file: {0} \n".format(filepath))
        
    
    


    # Open the ZED camera
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    positional_tracking_parameters.set_as_static = True
    cam.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()      # Define the Object Detection module parameters
    obj_param.enable_body_fitting = True            # Smooth skeleton move
    obj_param.enable_tracking = True                # Track people across images flow
    obj_param.image_sync = True                     # run detection for every Camera grab
    obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST  # Object detection model
    obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use
    obj_param.prediction_timeout_s = 0.2            # Defalt. The time taken before change from present to searching

    print("Object Detection: Loading Module...")
    err = cam.enable_object_detection(obj_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(err))
        cam.close()
        exit(1)

    # runtime parameters
    runtime = sl.RuntimeParameters(enable_depth=True)
    
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_param.detection_confidence_threshold = 40
    
    # Get ZED camera information
    camera_info = cam.get_camera_information()

    # 2D viewer utilities
    display_resolution = sl.Resolution(min(camera_info.camera_resolution.width, 1280), min(camera_info.camera_resolution.height, 720))
    
    image_scale = [display_resolution.width / camera_info.camera_resolution.width
                 , display_resolution.height / camera_info.camera_resolution.height]
    
    
    
    # Create ZED objects filled in the main loop
    bodies = sl.Objects()
    # Image holder
    mat = sl.Mat()

    # Font for displayed text
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Instructions
    print("============= INSTRUCTIONS ============= ")
    print("  Quit the video reading:      q")
    print("  Pause the video reading:     SPACE")
    print("  \t>>when paused, press (g) then enter frame number in the textbox to jump to certain frame.")
    print("  Restart the video: r")
    print("  Step forward:  [")
    print("  Step backward: ]")
    print("\n\n")

    # Main loop
    key = ''
    while key != 113:  # wait for 'q' key to exit the loop
        if not paused or key == 91 or key == 93 or key == ord('g') or key == ord('r'):
            # If not paused, or if (paused and stepped forward/backward)
            # then grab a frame to be viewed
            err = cam.grab(runtime)		  
        
        # On successful grab
        if err == sl.ERROR_CODE.SUCCESS:
            # Reteieve image
            cam.retrieve_image(mat, sl.VIEW.LEFT)
            # Retrieve objects
            cam.retrieve_objects(bodies, obj_runtime_param)

            frame = mat.get_data()
            
            # Put frame number and timestamp on the frame 
            cv2.putText(frame, f'Frame {cam.get_svo_position()}   |   Timestamp {cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()}',
                        (50, 50),
                        font, 
                        1, 
                        (0, 255, 255), 
                        2, 
                        cv2.LINE_4)
            tracking_viewer.render_2D(frame, image_scale,bodies.object_list, obj_param.enable_tracking, obj_param.body_format)
            
            # Show the frame
            cv2.imshow("ZED", frame)

            key = cv2.waitKey(1)

            # Decide what to do with the received key
            svo_controls(key) 
        else:
            key = cv2.waitKey(1)

    # Closing
    cv2.destroyAllWindows()
    mat.free(sl.MEM.CPU)
    print_camera_information(cam)
    cam.close()
    print("\nFINISH")


def svo_controls(key):
    global paused
    global cam
    
    # Choose action based on the pressed key
    if key == 32:                   # space key
        paused = not paused         # Pause/unpause
    
    if key == 114:                  # r key
        cam.set_svo_position(0)     # go back to frame zero
    
    if key == 91:                   # [ key: Go forward one frame at a time
        cam.set_svo_position(cam.get_svo_position()-1)
    
    if key == 93:                   # ] key: Go backward one frame at a time
        cam.set_svo_position(cam.get_svo_position()+1)
    
    # Only if paused:
    if paused and key == ord('g'):
        # If letter g is pressed: show a textbox, user can enter frame number and click go
        # Upon clicking go, the viewer will jump to that exact frame
        master = Tk()
        e = Entry(master)
        e.pack()
        e.focus_set()
        def callback():
             cam.set_svo_position(int(e.get()))
             master.destroy()
        b=Button(master, text='GO', width = 10, command=callback)
        b.pack()
        mainloop()


def print_camera_information(cam):
    print()
    print("Distorsion factor of the right cam before calibration: {0}.".format(
        cam.get_camera_information().calibration_parameters_raw.right_cam.disto))
    print("Distorsion factor of the right cam after calibration: {0}.\n".format(
        cam.get_camera_information().calibration_parameters.right_cam.disto))

    print("Confidence threshold: {0}".format(cam.get_runtime_parameters().confidence_threshold))
    print("Depth min and max range values: {0}, {1}".format(cam.get_init_parameters().depth_minimum_distance,
                                                            cam.get_init_parameters().depth_maximum_distance)
)
    print("Resolution: {0}, {1}.".format(round(cam.get_camera_information().camera_resolution.width, 2), cam.get_camera_information().camera_resolution.height))
    print("Camera FPS: {0}".format(cam.get_camera_information().camera_fps))
    print("Frame count: {0}.\n".format(cam.get_svo_number_of_frames()))

if __name__ == "__main__":
    main()
