# This script is not related to ZED camera, but we use it to calculate required
# time to transfer an array of shape (1, <win_size>, <n_dims>, <n_joints>, 1) 
# or any other shape, between two devices.

# =========================================================================== #
# Receiver Side ============================================================= #
import socket
import numpy as np
import pickle
import time
import struct
import signal 
import sys


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

# Add a Ctrl-C handler
signal.signal(signal.SIGINT, signal_handler)

# A flag to determine the behavior:
#   If True: calculate round trip time (send received data back to the client) 
#   If False: send back timestamp of receiving time
round_trip_behavior = False

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 12345

# Bind to the port
s.bind(('', port))

# Put the socket into listening mode
s.listen(5)

# To store round-trip times
print("Waiting for connection ... \n")
while True:
    round_trip_times = [] # Reset every time a new connection is established
    # Establish a connection with the client
    c, addr = s.accept()
    print('Got connection from', addr)
    print("Receiving ... \n")

    for _ in range(5000):
        # Start the timer
        start_time = time.time()

        # Receive the length of the data from the client first
        data_length = recvall(c, 4)
        print("Data length received: ", data_length, "\n")
        # data_length = struct.unpack('!I', data_length)[0]
        data_length = int.from_bytes(data_length, 'big')
        print("Data length unpacked: ", data_length, "\n")
  
        # Now receive the actual data
        print("Receiving data ... \n")
        data = recvall(c, data_length)
        print("Data received", "\n")
        # Unpickle the data to get the numpy array
        array = pickle.loads(data)

        if round_trip_behavior:
            # Send the data back to the client
            c.sendall(struct.pack('!I', data_length) + data)
            # Stop the timer
            end_time = time.time()
            # Calculate the round trip time
            round_trip_time = end_time - start_time
            # Store the round trip time
            round_trip_times.append(round_trip_time)
        else:
            # Send the timestamp back to the client
            c.sendall(struct.pack('!d', time.time()))
        

    # print time statistics
    if round_trip_behavior:
        print('Average round trip time: ', np.mean(round_trip_times[10:]))
        print('max round trip time: ', np.max(round_trip_times[10:]))

        for i, rtt in enumerate(round_trip_times):
            print("Round trip time ", i, ": ", rtt, "\n")
            if i == 6: break

    print("Done! \n")

    # Close the connection with the client
    c.close()
