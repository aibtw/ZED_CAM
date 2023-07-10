# import socket
# import numpy as np
# import pickle
# import struct

# def sendall(sock, data):
#     # Helper function to send all the data
#     bytes_sent = 0
#     while bytes_sent < len(data):
#         sent = sock.send(data[bytes_sent:])
#         if sent == 0:
#             raise RuntimeError("socket connection broken")
#         bytes_sent += sent

# def recvall(sock, n):
#     # Helper function to recv n bytes or return None if EOF is hit
#     data = b''
#     while len(data) < n:
#         packet = sock.recv(n - len(data))
#         if not packet:
#             return None
#         data += packet
#     return data

# # Create a socket object
# s = socket.socket()

# # Define the port on which you want to connect
# port = 12345

# # Connect to the server on the local computer
# s.connect(('192.168.100.79', port))

# # Create a numpy array
# array = np.random.random((1, 20, 3, 18, 1))

# # Pickle the numpy array to send it as a byte stream
# data = pickle.dumps(array)
# # data_length = struct.pack('!I', len(data))
# print("Data length: ", len(data), "\n")
# print("Data length in bytes: ", len(data).to_bytes(4, 'big'), "\n")
# data_length = len(data).to_bytes(4, 'big')

# # exit()
# print("Start Sending ... \n")
# for _ in range(100):
#     # Send the length of the data to the server first
#     # Then send the actual data
#     sendall(s, data_length + data)
#     print("Data Sent! \n")

#     # First receive the length of the data
#     print("Receiving the length of the data ... \n")
#     # received_data_length = struct.unpack('!I', s.recv(4))[0]
#     received_data_length = int.from_bytes(recvall(s, 4), 'big')
#     print("Data length received: ", received_data_length, "\n")

#     # Now receive the actual data
#     data = recvall(s, received_data_length)
#     print("data received! \n")
#     # Unpickle the data to get the numpy array
#     array = pickle.loads(data)

# # Close the connection
# s.close()



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
