import socket
import sys
import sqlite3
import threading
import time

# Set the IP address and port of the discovery server
discovery_server_ip = '172.20.10.5'
discovery_server_port = 5001

my_ip = '172.20.10.5'
my_port = 5001

def update_client(client_address, status):
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Update the status of the client in the client table
    c.execute("UPDATE client SET status = ? WHERE IP = ? AND port = ?", (status, client_address[0], client_address[1]))
    conn.commit()

    print(f"Updated client {client_address} status to {status}")

def register_client(client_address):
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Check if client already exists in client table
    c.execute("SELECT * FROM client WHERE IP = ? AND port = ?", (client_address[0], client_address[1]))
    client = c.fetchone()

    if client:
        # If client already exists, update the status to 'online'
        update_client(client_address, 'online')
    else:
        # If client doesn't exist, insert client into client table
        c.execute("INSERT INTO client (IP, port, status) VALUES (?, ?, ?)", (client_address[0], client_address[1], 'online'))
        conn.commit()

    # print(f"Registered new client {client_address}")

def list_online_clients():
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    # Retrieve the list of online clients from the client table
    c.execute("SELECT IP, port FROM client WHERE status = 'online'")
    clients = c.fetchall()

    # Create a list of client addresses in the format "IP:port"
    client_list = [f"{client[0]}:{client[1]}" for client in clients]

    return ",".join(client_list)

def handle_client(client_socket, client_address):
    conn = sqlite3.connect('p2p_chat.db')
    c = conn.cursor()

    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            if not message:
                break

            print(f'Received message from {client_address}: {message}')

            
            # Handle the request for a list of online clients
            if message == "list":
                response = list_online_clients()
                client_socket.send(response.encode())

            # Insert message into messages table
            else:
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

        # Break the loop if there is no message received
        if not message:
            break

    client_socket.close()

def keep_alive():
    # Send keep alive packet to discovery server every 10 seconds
    while True:
        try:
            keep_alive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            keep_alive_socket.connect((discovery_server_ip, discovery_server_port))
            # keep_alive_socket.send(f"Keep alive from {my_ip}:{my_port}".encode())
            keep_alive_socket.close()
            time.sleep(10)
        except socket.error as e:
            print(f"\nError sending keep alive packet to discovery server: {e}")
            time.sleep(10)

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

    # Start keep alive thread
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.start()

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            # print(f"New connection from {client_address}")

            # Register the new client
            register_client(client_address)

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

start_server()
