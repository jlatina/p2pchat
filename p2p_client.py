import socket
import sys
import sqlite3

conn = sqlite3.connect('p2p_chat.db')


IP = sys.argv[1]
PORT = int(sys.argv[2])

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

c = conn.cursor()

while True:
    message = input('Enter message: ')

    # Insert message into messages table
    c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (IP, PORT, message, 1))
    conn.commit()

    # send message to server
    client_socket.send(message.encode())

    response = client_socket.recv(1024).decode()
    print('Received:', response)
