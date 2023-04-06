import socket
import sys
import sqlite3
import threading

conn = sqlite3.connect('p2p_chat.db')

my_ip = '172.20.10.5'
my_port = 5000

c = conn.cursor()

# Prompt user for IP and port of second client
peer_ip = input("Enter IP address of other client: ")
peer_port = 5000

# Connect to other client
peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    peer_socket.connect((peer_ip, peer_port))
except socket.error as e:
    print(f"Error connecting to {peer_ip}:{peer_port}: {e}")
    sys.exit()

# Setup server socket to listen for incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((my_ip, my_port))
server_socket.listen()

def handle_client(client_socket):
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            print('Received:', message)

            # Insert message into messages table
            c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (peer_ip, my_port, message, 1))
            conn.commit()

            # Send response to client
            response = input('Enter response: ')
            client_socket.send(response.encode())

        except KeyboardInterrupt:
            print("\nKeyboard interrupt. Closing connection.")
            client_socket.close()
            break

        except socket.error as e:
            print(f"\nError sending/receiving data: {e}")
            client_socket.close()
            break

        except sqlite3.Error as e:
            print(f"\nError inserting data into database: {e}")
            client_socket.close()
            break

# Listen for incoming connections from other clients in a separate thread
def listen_for_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

client_listener_thread = threading.Thread(target=listen_for_clients)
client_listener_thread.start()

while True:
    try:
        message = input('Enter message: ')

        # Insert message into messages table
        c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (my_ip, peer_port, message, 1))
        conn.commit()

        # send message to other client
        peer_socket.send(message.encode())

    except KeyboardInterrupt:
        print("\nKeyboard interrupt. Closing connection.")
        peer_socket.close()
        server_socket.close()
        sys.exit()

    except socket.error as e:
        print(f"\nError sending/receiving data: {e}")
        peer_socket.close()
        server_socket.close()
        sys.exit()

    except sqlite3.Error as e:
        print(f"\nError inserting data into database: {e}")
        peer_socket.close()
        server_socket.close()
        sys.exit()