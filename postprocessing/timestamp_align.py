import csv 
import sys
import os
import numpy as np
import pandas as pd

# =============================================================== #
def main():
	print("Starting ...")
	# Process command line args
	argc = len(sys.argv)
	filespaths = []
	# Extract file names from args
	for i in range(1, argc):
		filepath = sys.argv[i]
		if not os.path.isfile(filepath): 
			print(f"[ERROR] Can't find file {filepath}\nPlease Enter a Correct Path")
			exit(1)
		filespaths.append(filepath)


	# ---------------------------------------------------------------------------- #
	# Read each file into a list of dictionaries, then put all of them into a list
	# ... So, one file = [{frame #: x, ts: y}, {frame #: x, ts: y}, ... etc]
	# ... And a list of files = [file1 data, file2 data ... etc]
	# ---------------------------------------------------------------------------- #
	list_of_files = []
	first_ts = []  # Hold the timestamp of the first frame from each file
	for f in filespaths:
		print(f"Reading File {f}")
		# Open CSV File 
		with open(f, 'r') as csv_file:
			dict_reader = csv.DictReader(csv_file)
			file_data = list(dict_reader)		# Convert the data into a list of dictionaries
			list_of_files.append(file_data)		# ... and append it to the list of files
			keys = list(file_data[-1].keys())  	# All column names of the current csv file
			timestamp_column_name = keys[1]    	# The name of the second column (contains timestamps)
			first_ts.append(int(file_data[0][timestamp_column_name])) # retrieve the timestamp of the first frame

	# Order the files in terms of their starting point (which file started recording first)
	order = np.argsort(first_ts) # ascending order
	# Determine the file that started last (the one with largest first timestamp), this will be the pivot file
	largest_ts_file = list_of_files[order[-1]]


	# ---------------------------------------------------------------------------------------------------- #
	# Calculate difference between each frame and previous frame. Add this as a seperate column called diff.
	# If the difference divided by the mean difference (16.67) is higher than 2 (a frame dropped) then ...
	# ... add an empty frame that is 16.67ms away from the previous one. 
	# ... Do this multiple times as needed.
	# ---------------------------------------------------------------------------------------------------- #
	new_list_of_files = [] 					# holder of all files after modifications
	for list_of_dict in list_of_files:		# loop over each list of dictionary in the list of files
		new_list_of_dict = []				# create a new list of dictionaries for each file
		
		for i in range(len(list_of_dict)): 	# loop over each dictionary (each frame) in the list 
			if i == 0: 						# first frame: zero difference (no frame before it)
				diff = 0					
			else: 							# otherwise: calc time diff between current and previous frame
				diff = int(list_of_dict[i][timestamp_column_name]) - int(list_of_dict[i-1][timestamp_column_name]) 

			ratio = diff / 16.67			# this should return how many frames were dropped, approxamatly

			# Here we deal with each dropped frame by adding a spece holder for each of them.
			# If round(ratio) = 2 then diff might have been between 26-41.
			# ... On average, difference is 16.67,
			# ... thus, we need to add only one frame,
			# ... which is equal to round(ratio) - 1.
			# ... This is applicable for any round(ratio) >= 2,
			# ... which is why we will loop over range(round(ratio)-1)
			if round(ratio) >= 2:
				for j in range(round(ratio)-1):
					row = list_of_dict[i].copy()	# Copy current list_of_dict row and modify it as a dropped frame
					row[timestamp_column_name] = np.uint64(list_of_dict[i-1][timestamp_column_name]) + (16.67*(j+1))
					row['diff'] = ""
					new_list_of_dict.append(row)	# Append the modified row into new_data_dict

			# After adding dropped frames holders (if there was any)
			list_of_dict[i]['diff'] = diff				# modify the current frame
			new_list_of_dict.append(list_of_dict[i])	# and append it to new_data_dict
		
		new_list_of_files.append(new_list_of_dict) # Append the new list of dictionaries to the new list of files.
	
	
	# for each file, find a frame corresponding to the first frame in the largest ts file.
	starting_frames = []  # To hold the new starting frame of each file
	for i, list_of_dict in enumerate(new_list_of_files):
		# If the current file is the one that started last, append 0 (its frames won't be shifted)
		if i == order[-1]: 
			starting_frames.append(0)
			continue
		
		# Otherwise, find the suitable corresponding frame by comparing each frame's timestamp with the pivot file timestamp
		diff = np.inf
		for j, frame in enumerate(list_of_dict):
			old_diff = diff
			diff = first_ts[order[-1]] - int(frame[keys[1]])
			if  diff <= 8 and diff < old_diff:
				starting_frames.append(j)
				break
	print(starting_frames)

	for i, filepath in enumerate(filespaths):
		# File name (without path)
		filename = os.path.basename(filepath)
		# The name of the output file
		newfilename = filename.replace('.csv', '_aligned.csv')
		# The *parent* directory of the *parent* directory the file was in
		basedire = os.path.dirname(os.path.dirname(filepath))
		# Making a new directory to store output csv at
		newdir = os.path.join(basedire, 'aligned')
		if not os.path.exists(newdir):
			os.mkdir(newdir)

		starting_frame = int(starting_frames[i])
		new_list_of_dict = new_list_of_files[i][starting_frame:]
		with open(os.path.join(newdir, newfilename), 'w') as csv_file: 
			dict_writer = csv.DictWriter(csv_file, new_list_of_dict[-1].keys())
			dict_writer.writeheader()
			dict_writer.writerows(new_list_of_dict)




if __name__ == '__main__':
	main()
