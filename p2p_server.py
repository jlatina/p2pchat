import socket
import threading
import sqlite3
import time

IP_ADDRESS = '172.20.10.5' # Replace with your IP address
PORT = 5001

MESSAGE_TYPE_KEEP_ALIVE = "keep alive"
MESSAGE_TYPE_LIST_CLIENTS = "list clients"
MESSAGE_TYPE_CHAT = "chat"

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP_ADDRESS, PORT))
        self.server_socket.listen()

        self.clients = {}

        self.sync_lock = threading.Lock()

        conn = sqlite3.connect('p2p_chat.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (sender text, recipient text, message text, timestamp real)''')
        conn.commit()
        conn.close()

    def start(self):
        print(f"Server started on {IP_ADDRESS}:{PORT}")

        while True:
            # Wait for a new client to connect
            client_socket, address = self.server_socket.accept()
            print(f"New client connected: {address}")

            # Add the new client to the dictionary of clients
            with self.sync_lock:
                self.clients[client_socket] = address

            # Start a new thread to handle messages from the client
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        conn = sqlite3.connect('p2p_chat.db')
        c = conn.cursor()

        while True:
            # Wait for a message from the client
            try:
                message = client_socket.recv(1024).decode()
            except socket.error as e:
                print(f"Error receiving message from {self.clients[client_socket]}: {e}")
                break

            # Check if the message is a keep alive message
            if message == MESSAGE_TYPE_KEEP_ALIVE:
                continue

            # Check if the message is a request for the list of clients
            if message == MESSAGE_TYPE_LIST_CLIENTS:
                client_list = [str(address) for address in self.clients.values()]
                client_list_str = "\n".join(client_list)
                client_socket.send(MESSAGE_TYPE_LIST_CLIENTS.encode())
                client_socket.send(client_list_str.encode())
                continue

            # If the message is not a special message
            sender_address = self.clients[client_socket]
            with self.sync_lock:
                for socket, address in self.clients.items():
                    if socket != client_socket:
                        #socket.send(MESSAGE_TYPE_CHAT.encode())
                        socket.send(message.encode())

            # Store the message in the database
            timestamp = time.monotonic()
            c.execute("INSERT INTO messages (sender, receiver, msg, time) VALUES (?, ?, ?, ?)",
                      (sender_address[0], "all", message, timestamp))

            conn.commit()

        # Remove the client from the dictionary of clients
        with self.sync_lock:
            del self.clients[client_socket]

        # Close the client socket
        client_socket.close()

        print(f"Client {self.clients[client_socket]} disconnected")

if __name__ == "__main__":
    server = Server()
    server.start()
