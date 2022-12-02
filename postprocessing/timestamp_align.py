import csv 
import sys
import os
import numpy as np

# =============================================================== #
def main():
	print("Starting ...")
	# Process command line args
	argc = len(sys.argv)
	file_names = []
	# Extract file names from args
	for i in range(1, argc):
		file_name = sys.argv[i]
		if not os.path.isfile(file_name): 
			print(f"[ERROR] Can't find file {file_name}\nPlease Enter a Correct Path")
			exit(1)
		file_names.append(file_name)


	# ---------------------------------------------------------------------------- #
	# Read each file into a list of dictionaries, then put all files into a list
	# ... So, one file = [{frame #: x, ts: y}, {frame #: x, ts: y}, ... etc]
	# ... And a list of files = [file1, file2 ... etc]
	# ---------------------------------------------------------------------------- #
	list_of_files = []
	first_ts = []  # Hold the timestamp of the first frame from each file
	for f in file_names:
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
	# for each file, find a frame corresponding to the first frame in the largest ts file.
	starting_frames = []  # To hold the new starting frame of each file
	for i, file in enumerate(list_of_files):
		# If the current file is the one that started last, append 0 (its frames won't be shifted)
		if i == order[-1]: 
			starting_frames.append(0)
			continue
		
		# Otherwise, find the suitable corresponding frame by comparing each frame's timestamp with the pivot file timestamp
		diff = np.inf
		for frame in file:
			old_diff = diff
			diff = first_ts[order[-1]] - int(frame[keys[1]])
			if  diff <= 8 and diff < old_diff:
				starting_frames.append(frame[keys[0]])
				break

	print(starting_frames)

	# write the files again after ffa (first frame aligned)
	for i, file_name in enumerate(file_names):
		starting_frame = int(starting_frames[i])
		new_data_dict = list_of_files[i][starting_frame:]
		with open(file_name.replace('.csv', '_ffa.csv'), 'w') as csv_file: 
			dict_writer = csv.DictWriter(csv_file, new_data_dict[-1].keys())
			dict_writer.writeheader()
			dict_writer.writerows(new_data_dict)




if __name__ == '__main__':
	main()
