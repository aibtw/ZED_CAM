import sys
import os
import argparse
import csv
import subprocess

'''
This program takes in an svo file, and a csv file containing timestamps for each frame.
The csv file columns are assumed to be ["frame #", "timestamp", "dropped frames"],
The svo file will then be cut, based on first and last frame number in the csv file.
For inputting multiple files, the svo and csv files must be entered respectively (svo1, svo2, svo3, csv1, csv2, csv3)

This program assumes the presence of /usr/local/zed/tools/ZED_SVO_EDITOR file. 
The output is going to be saved in path-to-input-svo/cut_svo.
'''

def main():
    parser = argparse.ArgumentParser(prog='This program takes input svo and its timestamps csv file,'+
                                            ' and will cut both ends of the svo based on the csv file')

    parser.add_argument('-v', '--video', nargs='*', help='Path to svo file')
    parser.add_argument('-t', '--timestamps', nargs='*', help='Path to csv file corresponding to svo file')

    # Arg parse
    args = parser.parse_args()
    videospaths = args.video
    tspaths = args.timestamps

    # make sure a corresponding timestamp file is present for each svo file.
    if len(videospaths) != len(tspaths):
        print("Please enter a csv file corresponding to the input svo file")

    processes = []  # a holder for ZED_SVO_Editor process/es

    # Loop over each input svo file
    for i in range(len(videospaths)):
        print("Reading SVO file: {0} \n".format(videospaths[i]))
        # Read the csv file
        with open(tspaths[i], 'r') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            file_data = list(dict_reader)		# Convert the data into a list of dictionaries
            keys = list(file_data[-1].keys())  	# All column names of the current csv file
            id_column = keys[0]    	            # The name of the second column (contains timestamps)

        # File name (without path)
        filename = os.path.basename(videospaths[i])
        # The name of the output file
        newfilename = filename.replace('.svo', '_cut.svo')
        # The *parent* directory of the file was in
        basedire = os.path.dirname(videospaths[i])
        # Making a new directory to store output svo at
        newdir = os.path.join(basedire, 'cut_svo')
        if not os.path.exists(newdir):
            os.mkdir(newdir)

        # Start a ZED_SVO_Editor process
        processes.append(subprocess.Popen(['/usr/local/zed/tools/ZED_SVO_Editor',
                                            '-cut',
                                            videospaths[i],
                                            '-s', 
                                            file_data[0][id_column],
                                            '-e',
                                            file_data[-1][id_column],
                                            os.path.join(newdir, newfilename)]))
        print(f'Started processing file {i}')

    for i,process in enumerate(processes):
        process.wait()
        print(f'Finished processing file {i}')
    print('Done')




if __name__ == '__main__': 
    main()