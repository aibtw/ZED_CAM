#!/usr/bin/python3
import sys
import cv2
from tkinter import *
import pyzed.sl as sl

paused = False
cam = sl.Camera()

def main():
    global paused
    global cam

    print("\nSTARTING ...\n")

    # Arg parse
    if len(sys.argv) != 2:
        print("Please specify path to .svo file.")
        exit()
    filepath = sys.argv[1]
    print("Reading SVO file: {0} \n".format(filepath))

    # Init camera and open it
    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    # runtime parameters
    runtime = sl.RuntimeParameters(enable_depth=True)
    
    # Frames holder
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
            cam.retrieve_image(mat, sl.VIEW.LEFT)
            frame = mat.get_data()
            
            # Put frame number and timestamp on the frame 
            cv2.putText(frame, f'Frame {cam.get_svo_position()}   |   Timestamp {cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()}',
                        (50, 50),
                        font, 
                        1, 
                        (0, 255, 255), 
                        2, 
                        cv2.LINE_4)
            
            # Show the frame
            cv2.imshow("ZED", frame)

            key = cv2.waitKey(1)

            # Decide what to do with the received key
            svo_controls(key) 
        else:
            key = cv2.waitKey(1)

    # Closing
    cv2.destroyAllWindows()
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
