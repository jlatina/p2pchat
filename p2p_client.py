import socket
import sys
import sqlite3

conn = sqlite3.connect('p2p_chat.db')

# Prompt user for IP and port of second client
peer_ip = input("Enter IP address of other client: ")
peer_port = int(input("Enter port of other client: "))

# Connect to other client
peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    peer_socket.connect((peer_ip, peer_port))
except socket.error as e:
    print(f"Error connecting to {peer_ip}:{peer_port}")
    sys.exit()

# Get IP and port of current client
if len(sys.argv) < 3:
    print("Usage: python p2p_client.py <IP address> <port>")
    sys.exit()

my_ip = sys.argv[1]
my_port = int(sys.argv[2])

c = conn.cursor()

while True:
    try:
        message = input('Enter message: ')

        # Insert message into messages table
        c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (my_ip, peer_port, message, 1))
        conn.commit()

        # send message to other client
        peer_socket.send(message.encode())

        response = peer_socket.recv(1024).decode()
        print('Received:', response)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt. Closing connection.")
        peer_socket.close()
        sys.exit()

    except socket.error as e:
        print(f"\nError sending/receiving data: {e}")
        peer_socket.close()
        sys.exit()

    except sqlite3.Error as e:
        print(f"\nError inserting data into database: {e}")
        sys.exit()
