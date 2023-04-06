import socket
import sqlite3
import select
import time

my_ip = '172.20.10.5' # Replace with your IP address
my_port = 5001

peer_ip = '172.20.10.5' # Replace with server IP address
peer_port = 5001 # Replace with server port

KEEP_ALIVE_INTERVAL = 30 # in seconds
MESSAGE_TYPE_LIST_CLIENTS = "list clients"
MESSAGE_TYPE_CHAT = "chat"
MESSAGE_TYPE_UPDATE = "update"


def start_client():
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Connect to server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.connect((peer_ip, peer_port))
    except socket.error as e:
        print(f"Error connecting to {peer_ip}:{peer_port}: {e}")
        return

    # Send keep alive message every KEEP_ALIVE_INTERVAL seconds
    last_keep_alive_time = time.monotonic()
    first_entry = True

    while True:
        # Prompt user for message to send
        if not first_entry:
            message = input("Enter message (or type 'quit' to exit, 'list' to request a list of clients): ")
        else:
            message = ""

        # Exit the loop if the user enters 'quit'
        if message == 'quit':
            break

        if message == 'list':
            server_socket.send(MESSAGE_TYPE_LIST_CLIENTS.encode())

        # Send message to server
        recipient_ip = input("Enter recipient IP address: ")
        message_text = input("Enter message: ")
        message_type = MESSAGE_TYPE_CHAT
        sender = my_ip
        recipient = recipient_ip
        message = f"{message_text}"

         # Check if it's time to send a keep alive message
        current_time = time.monotonic()
        if current_time - last_keep_alive_time >= KEEP_ALIVE_INTERVAL:
            server_socket.send("keep alive".encode())
            last_keep_alive_time = current_time

        # Wait for up to 5 seconds for a response
        ready = select.select([server_socket], [], [], 5)
        if ready[0]:
            response = server_socket.recv(1024).decode()
            if response == MESSAGE_TYPE_LIST_CLIENTS:
                # Receive the list of clients
                client_list = server_socket.recv(1024).decode()
                print(f"Client list: {client_list}")
            else:
                print(f"Server response: {response}")
        else:
            print("No response received from server")

    server_socket.close()

start_client()
