import socket
import select
import pickle

HEADERSIZE = 10
IP = '127.0.0.1'
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))
server.listen()

sockets_list = [server]
clients = {} #dict of clients/connections sockets and addressess
print(f'Listening for connections on {IP}:{PORT}...')

#Receieves message with a header attached
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADERSIZE)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8'))
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    #Loops through sockets that are waiting to be read
    for notified_socket in read_sockets:
        #New connection
        if notified_socket == server:
            #Stores socket, address and username
            client_socket, client_address = server.accept()
            user = receive_message(client_socket)    
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
        #Returning connection
        else:
            #Recieves message 
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
     ##Loops through sockets that are throwing and exception
    for notified_socket in exception_sockets:
        #Removes from user from list of connections/clients
        sockets_list.remove(notified_socket)
        del clients[notified_socket]