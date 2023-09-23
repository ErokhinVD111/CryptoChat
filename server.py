import socket
import select
from typing import  Any

from configuration import Configuration, get_config


class Server:
    def __init__(self, config: Configuration):
        self._clients = None
        self._sockets_list = None
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._ip = config.server["ip"]
        self._port = int(config.server["port"])
        self._header_length = int(config.message["header_length"])
        self._server_socket.bind((self._ip, self._port))

    def start(self):
        self._server_socket.listen()
        self._sockets_list = [self._server_socket]
        self._clients = {}
        print(f'Listening for connections on {self._ip}:{self._port}...')
        self._listen()

    def _receive_message(self, client_socket) -> bool | dict[str, Any]:
        header_length = self._header_length
        try:
            message_header = client_socket.recv(header_length)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def _listen(self):
        def handle_new_connection() -> bool:
            client_socket, client_address = self._server_socket.accept()
            user = self._receive_message(client_socket)
            if user is False:
                return False
            self._sockets_list.append(client_socket)
            self._clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user['data'].decode('utf-8')))
            return True

        def handle_existing_connection(socket) -> bool:
            message = self._receive_message(socket)
            if message is False:
                print('Closed connection from: {}'.format(
                    self._clients[socket]['data'].decode('utf-8')))
                self._sockets_list.remove(socket)
                del self._clients[socket]
                return False
            user = self._clients[socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            for client_socket in self._clients:
                if client_socket != socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
            return True

        def handle_exception_connection(socket):
            self._sockets_list.remove(socket)
            del self._clients[socket]

        while True:
            read_sockets, _, exception_sockets = select.select(self._sockets_list, [], self._sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self._server_socket:
                    if not handle_new_connection():
                        continue
                else:
                    if not handle_existing_connection(notified_socket):
                        continue

            for notified_socket in exception_sockets:
                handle_exception_connection(notified_socket)


if __name__ == "__main__":
    config = get_config()
    server = Server(config)
    server.start()
