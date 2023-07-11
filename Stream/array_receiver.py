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

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 12345

# Bind to the port
s.bind(('', port))

# Put the socket into listening mode
s.listen(5)

# To store round-trip times
round_trip_times = []

print("Waiting for connection ... \n")
while True:
    # Establish a connection with the client
    c, addr = s.accept()
    print('Got connection from', addr)
    print("Receiving ... \n")
    for _ in range(100):
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

        # Send the data back to the client
        c.sendall(struct.pack('!I', data_length) + data)

        end_time = time.time()
        round_trip_time = end_time - start_time
        round_trip_times.append(round_trip_time)

    print('Average round trip time: ', np.mean(round_trip_times))

    # Close the connection with the client
    c.close()