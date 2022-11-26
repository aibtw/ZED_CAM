import sys
import pyzed.sl as sl
import cv2
from tkinter import *


paused=False
cam = sl.Camera()

def main():
    global paused
    global cam

    if len(sys.argv) != 2:
        print("Please specify path to .svo file.")
        exit()

    filepath = sys.argv[1]
    print("Reading SVO file: {0}".format(filepath))

    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime = sl.RuntimeParameters(enable_depth=False)
    mat = sl.Mat()
    font = cv2.FONT_HERSHEY_SIMPLEX

    key = ''
    print("  Save the current image:      s")
    print("  Quit the video reading:      q")
    print("  Pause the video reading:     SPACE")
    print("  Restart the video reading:   r")
    print("  Step forward:   		  [")
    print("  Step backward: 		  ]")
    print("  when : 		  ]")
    
    
    print("\n\n")


    while key != 113:  # for 'q' key
        if not paused or key == 91 or key == 93 or key == ord('g'):  # Not paused, or paused but pressed '[' or ']' which are step forward/backward
            err = cam.grab(runtime)		  # Grab a frame to be viewed
        
        if err == sl.ERROR_CODE.SUCCESS:
            cam.retrieve_image(mat)
            frame = mat.get_data()
            
            cv2.putText(frame, f'Frame {cam.get_svo_position()}   |   Timestamp {cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()}',
                        (50, 50),
                        font, 
                        1, 
                        (0, 255, 255), 
                        2, 
                        cv2.LINE_4)
            
            cv2.imshow("ZED", frame)

            key = cv2.waitKey(1)
            # saving_image(key, mat)
            svo_controls(key) 
        else:
            key = cv2.waitKey(1)
    cv2.destroyAllWindows()

    # print_camera_information(cam)
    cam.close()
    print("\nFINISH")


def svo_controls(key):
    global paused
    global cam
    
    if key == 32: # space
        paused = not paused
    if key == 114: # r
        cam.set_svo_position(0)
    if key == 91: # [
        cam.set_svo_position(cam.get_svo_position()-1)
    if key == 93: # ]
        cam.set_svo_position(cam.get_svo_position()+1)
    if paused and key == ord('g'):
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


def saving_image(key, mat):
    if key == 115:
        img = sl.ERROR_CODE.FAILURE
        while img != sl.ERROR_CODE.SUCCESS:
            filepath = input("Enter filepath name: ")
            img = mat.write(filepath)
            print("Saving image : {0}".format(repr(img)))
            if img == sl.ERROR_CODE.SUCCESS:
                break
            else:
                print("Help: you must enter the filepath + filename + PNG extension.")


def print_camera_information(cam):
    while True:
        res = input("Do you want to display camera information? [y/n]: ")
        if res == "y":
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
            break
        elif res == "n":
            print("Camera information not displayed.\n")
            break
        else:
            print("Error, please enter [y/n].\n")


if __name__ == "__main__":
    main()
