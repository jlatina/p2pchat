import socket
import sqlite3

conn = sqlite3.connect('p2p_chat.db')


# Define the IP address and port number for the server
IP = '127.0.0.1'
PORT = 5001

# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen(2)
print('Waiting for connections...')

# Accept connections from two clients
client1, address1 = server_socket.accept()
print('Connection established with', address1)
client2, address2 = server_socket.accept()
print('Connection established with', address2)

# Send and receive messages between the clients
while True:
    # Receive a message from client 1 and send it to client 2
    message = client1.recv(1024).decode()
    client2.send(message.encode())

    # Receive a message from client 2 and send it to client 1
    message = client2.recv(1024).decode()
    client1.send(message.encode())