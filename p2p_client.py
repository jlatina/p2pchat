import socket
import sys

IP = sys.argv[1]
PORT = int(sys.argv[2])

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

while True:
    message = input('Enter message: ')
    client_socket.send(message.encode())

    response = client_socket.recv(1024).decode()
    print('Received:', response)
