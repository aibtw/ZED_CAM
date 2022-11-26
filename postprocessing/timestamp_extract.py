import sys
import csv
import pyzed.sl as sl
from tkinter import *



def main():
    # Arg Parsing
    if len(sys.argv) != 2:
        print("Please specify path to .svo file.")
        exit()
    filepath = sys.argv[1]
    print("Reading SVO file: {0}".format(filepath))

    # Init camera
    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    # Runtime parameters
    runtime = sl.RuntimeParameters(enable_depth=False)

    # List to hold every {frame #, timestamp}
    out_data = []

    while True:
        # Grab a frame
        err = cam.grab(runtime)

        # Successful grab
        if err == sl.ERROR_CODE.SUCCESS:
            # Get timestamp
            timestamp = cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()
            # Get frame number
            fn = cam.get_svo_position()
            # Record timestamp in list
            out_data.append({'#': fn, 'timestamp': timestamp})

            if fn % 1000 == 0:
                print(fn)

        # End of file reached
        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED: 
            break

    # Closing camera
    cam.close()
    
    # Write csv file
    with open(filepath.replace('.svo', '_timestamps.csv'), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ['#', 'timestamp'])
        writer.writeheader()
        writer.writerows(out_data)
    


    print("\nFINISH")


if __name__ == "__main__":
    main()
