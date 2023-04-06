import socket
import sys
import sqlite3

my_ip = '172.20.10.5' # Replace with your IP address
my_port = 5000

peer_ip = '172.20.10.7' # Replace with server IP address
peer_port = 5001 # Replace with server port

def start_client():
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Prompt user for message to send
    message = input("Enter message: ")

    # Connect to server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.connect((peer_ip, peer_port))
    except socket.error as e:
        print(f"Error connecting to {peer_ip}:{peer_port}: {e}")
        sys.exit()

    # Send message to server
    server_socket.send(message.encode())

    # Receive response from server
    response = server_socket.recv
