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


def sendall(sock, data):
    # Helper function to send all the data
    bytes_sent = 0
    while bytes_sent < len(data):
        sent = sock.send(data[bytes_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        bytes_sent += sent

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

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 12345

# Connect to the server on the local computer
# s.connect(('192.168.100.59', port)) # Jetson
s.connect(('localhost', port))

# Create a numpy array
array = np.random.random((1, 40, 3, 18, 1))

# Pickle the numpy array to send it as a byte stream
data = pickle.dumps(array)
# data_length = struct.pack('!I', len(data))
print("Data length: ", len(data), "\n")
print("Data length in bytes: ", len(data).to_bytes(4, 'big'), "\n")
data_length = len(data).to_bytes(4, 'big')

# exit()
round_trip_times = []
print("Start Sending ... \n")
for _ in range(100):
    # Send the length of the data to the server first
    # Then send the actual data
    start_time = time.time()
    sendall(s, data_length + data)
    print("Data Sent! \n")

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

    end_time = time.time()
    # Calculate the round-trip time
    round_trip_time = end_time - start_time
    round_trip_times.append(round_trip_time)

# print('Average round trip time: ', np.mean(round_trip_times))
print('Average round trip time: ', np.mean(round_trip_times[5:]))
print('max round trip time: ', np.max(round_trip_times[5:]))

for i, rtt in enumerate(round_trip_times):
    print("Round trip time ", i, ": ", rtt, "\n")
    if i == 6: break

# Close the connection
s.close()

# Plot the round-trip times
plt.plot(round_trip_times)
plt.xlabel('Iteration')
plt.ylabel('Round-trip time (s)')
plt.show()