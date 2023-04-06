import socket
import sys
import sqlite3
import threading

my_ip = '172.20.10.5'
my_port = 5001

def handle_client(client_socket, client_address):
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()
    

    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            print(f'Received message from {client_address}: {message}')

            # Insert message into messages table
            c.execute("INSERT INTO messages (sender, receiver, msg, time, isSent) VALUES (?, ?, ?, datetime('now'), ?)", (client_address[0], my_port, message, 1))
            conn.commit()

            # Send response to client
            client_socket.send("Message received".encode())

        except KeyboardInterrupt:
            print("\nKeyboard interrupt. Closing connection.")
            client_socket.close()
            sys.exit()

        except socket.error as e:
            print(f"\nError sending/receiving data: {e}")
            client_socket.close()
            sys.exit()

        except sqlite3.Error as e:
            print(f"\nError inserting data into database: {e}")
            client_socket.close()
            sys.exit()

def start_server():
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Create messages table if it doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS messages (sender TEXT, receiver TEXT, msg TEXT, time TEXT, isSent INTEGER)")
    conn.commit()

    # Listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((my_ip, my_port))
    server_socket.listen()

    print(f"Server listening on {my_ip}:{my_port}")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"New connection from {client_address}")
            # Handle the new client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

        except KeyboardInterrupt:
            print("\nKeyboard interrupt. Closing server.")
            server_socket.close()
            sys.exit()

        except socket.error as e:
            print(f"\nError accepting connection: {e}")
            server_socket.close()
            sys.exit()
        except (ConnectionResetError, ConnectionAbortedError):
            print("\nClient disconnected. Closing socket.")
            client_socket.close()


start_server()
