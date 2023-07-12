# This script is not related to ZED camera, but we use it to calculate required
# time to transfer an array of shape (1, <win_size>, <n_dims>, <n_joints>, 1) 
# or any other shape, between two devices.

# =========================================================================== #
# Sender Side =============================================================== #
import socket
import numpy as np
import pickle
import struct
import time
import signal
import sys
import matplotlib.pyplot as plt


# Helper functions ========================================================== #
def sendall(sock, data):
    """ Helper function to send all the data """
    bytes_sent = 0                                   # Number of bytes sent
    while bytes_sent < len(data):                    # While not all data sent
        sent = sock.send(data[bytes_sent:])          # Send some more data
        if sent == 0:                                # Socket connection broken
            raise RuntimeError("socket connection broken")
        bytes_sent += sent                           # Update bytes sent          

def recvall(sock, n):
    """ Helper function to recv n bytes or return None if EOF is hit """
    data = b''                                      # Empty byte string
    while len(data) < n:                            # while not all data received 
        packet = sock.recv(n - len(data))           # Receive some more data
        if not packet:                              # Socket connection broken
            return None                             
        data += packet                              # Update data
    return data

def signal_handler(sig, frame):
    """ Ctrl-C handler """
    print('You pressed Ctrl+C!')
    sys.exit(0)

# Add a Ctrl-C handler ====================================================== #
signal.signal(signal.SIGINT, signal_handler)

# A flag to determine the behavior: ----------------------------------------- #
#   If True: calculate round trip time (send received data back to the client) 
#   If False: send back timestamp of receiving time
round_trip_behavior = False

# socket -------------------------------------------------------------------- #
s = socket.socket()
port = 12345
s.connect(('localhost', port)) # Connect to the server on the local computer
# s.connect(('192.168.100.59', port)) # Jetson

# Create a numpy array to send ---------------------------------------------- #
# array = np.random.random((1, 40, 3, 18, 1))  # Skeleton array
array = np.random.random((2,1,10)) # model output array (n_people, 1, n_classes)

# Pickle the numpy array to send it as a byte stream ------------------------ #
data = pickle.dumps(array)

# prepare the length of the data to send ------------------------------------ #
# data_length = struct.pack('!I', len(data))
print("Data length: ", len(data), "\n")
print("Data length in bytes: ", len(data).to_bytes(4, 'big'), "\n")
data_length = len(data).to_bytes(4, 'big')

round_trip_times = [] # To store round-trip times --------------------------- #
transfer_time = [] # To store one-direction transfer times ------------------ #

# Send the data ------------------------------------------------------------- #
print("Start Sending ... \n")
for _ in range(5000):
    # Send the length of the data to the server first ....................... #
    # Then send the actual data ............................................. #
    # Start the timer ....................................................... #
    start_time = time.time()
    sendall(s, data_length + data)
    print("Data Sent! \n")

    if round_trip_behavior: # ............................................... #
        # First receive the length of the data 
        print("Receiving the length of the data ... \n")
        # received_data_length = struct.unpack('!I', s.recv(4))[0]
        received_data_length = int.from_bytes(recvall(s, 4), 'big')
        print("Data length received: ", received_data_length, "\n")

        # Now receive the actual data
        data = recvall(s, received_data_length)
        print("data received! \n")
        # Unpickle the data to get the numpy array
        array = pickle.loads(data)
        # stop the timer
        end_time = time.time()
        # Calculate the round-trip time
        round_trip_time = end_time - start_time
        round_trip_times.append(round_trip_time)

    else: # ................................................................. #
        # Receive the timestamp of receiving time
        print("Receiving the timestamp of receiving time ... \n")
        received_time = struct.unpack('!d', s.recv(8))[0]
        print("Received time: ", received_time, "\n")
        transfer_time.append(received_time - start_time)

# Close the connection
s.close()

if round_trip_behavior: # --------------------------------------------------- #
    # Print time statistics
    print('Average round trip time: ', np.mean(round_trip_times))
    print('max round trip time: ', np.max(round_trip_times))
    # Print the first few round-trip times
    for i, rtt in enumerate(round_trip_times):
        print("Round trip time ", i, ": ", rtt, "\n")
        if i == 6: break
    # Plot the round-trip times
    plt.plot(round_trip_times)
    plt.xlabel('Iteration')
    plt.ylabel('Round-trip time (s)')
    plt.show()
else: # --------------------------------------------------------------------- #
    # Print time statistics
    print('Average transfer time: ', np.mean(transfer_time))
    print('max transfer time: ', np.max(transfer_time))
    # Print the first few transfer times
    for i, tt in enumerate(transfer_time):
        print("Transfer time ", i, ": ", tt, "\n")
        if i == 6: break
    # Plot the transfer times
    plt.plot(transfer_time)
    plt.xlabel('Iteration')
    plt.ylabel('Transfer time (s)')
    plt.show()




