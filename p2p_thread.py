import threading
import socket
import time

class ClientThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.online = False

    def run(self):
        while True:
            try:
                # create a socket and connect to the client
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.ip, self.port))

                # send a heartbeat message to the client
                heartbeat_msg = 'HEARTBEAT'
                client_socket.send(heartbeat_msg.encode())

                # wait for a response from the client
                response = client_socket.recv(1024).decode()

                # set the online status based on the response
                if response == 'ACK':
                    self.online = True
                else:
                    self.online = False

                # close the socket
                client_socket.close()

            except Exception as e:
                # if there's an error, assume the client is offline
                self.online = False

            # wait for 10 seconds before sending the next heartbeat message
            time.sleep(10)

# create a list of client threads
client_threads = []

# add clients to the list
client1 = ClientThread('192.168.1.100', 5000)
client_threads.append(client1)

client2 = ClientThread('192.168.1.101', 5000)
client_threads.append(client2)

# start the client threads
for client_thread in client_threads:
    client_thread.start()

# continuously print the online status of each client
while True:
    for client_thread in client_threads:
        print(f'Client {client_thread.ip}:{client_thread.port} is {"online" if client_thread.online else "offline"}')
    time.sleep(1)
