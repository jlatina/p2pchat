import socket
import sys
import sqlite3

conn = sqlite3.connect('p2p_chat.db')

# Prompt user for IP and port of second client
peer_ip = input("Enter IP address of other client: ")
peer_port = int(input("Enter port of other client: "))

# Connect to other client
peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
peer_socket.connect((peer_ip, peer_port))

# Get IP and port of current client
my_ip = sys.argv[1]
my_port = int(sys.argv[2])

c = conn.cursor()

while True:
    message = input('Enter message: ')

    # Insert message into messages table
    c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (my_ip, peer_port, message, 1))
    conn.commit()

    # send message to other client
    peer_socket.send(message.encode())

    response = peer_socket.recv(1024).decode()
    print('Received:', response)
