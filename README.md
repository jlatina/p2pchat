# Simple P2P chat application
by Lesly Alcantara & Jeanette Villanueva

Purpose: Allows clients to connect to a server and exchange messages w/ each other.

Server: Manages connections between clients, forwarding messages from one client to another

Functionality:
* Creates a TCP Socket
* Server listens for incoming connections
* When a new client connects to the server, the servercs accepts the connection
* Then, the server adds the new client to a dictionary of clients, w/ the key being the client socket obcjet and the value being the client address.
* Server now starts a new thread to handle messages from client by calling `handle_client()` method
  * This method runs in a loop and waits for messages from the client
  * If the message is a keep-alive message, the method continues to wait for new messages
  * If the message is a request for list of clients = give list from dictionary
  * If message is a chat message, the server forwards the message to all other clients (except the one that sent it)
  * Also stores chat hustory in a SQLite DB by inserting a new row into the messages table.
 * Error handling: If error occurs while receiving message from client -> Server removes the client from the dict of clients and closes the client socke


Client: Can connect to the server and initiate a chat with other clients by sending messages to the server

Functionality:
* Creates a TCP socket 
* Connects to server
* Enters a loop that prompts the user to enter a message
* If message = list -> Return list
* If message = chat -> Prompts to enter the recepient IP address and message text
  * Client sends chat message to the server
  * Client also sends a keep-alive message to the server every 30 seconds to prevent the connection from being closed due to inactivity
  * Client waits for up to 5 seconds for a response from server. If server sends a response, the client prints into console.
