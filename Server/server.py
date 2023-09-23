import socket
import select
from typing import Dict, Any

from Config.configuration import Configuration


class Server:
    def __init__(self, config: Configuration):
        self.__clients = None
        self.__sockets_list = None
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__ip = config.server["ip"]
        self.__port = int(config.server["port"])
        self.__header_length = int(config.message["header_length"])
        self.__server_socket.bind((self.__ip, self.__port))

    def start(self):
        self.__server_socket.listen()
        self.__sockets_list = [self.__server_socket]
        self.__clients = {}
        print(f'Listening for connections on {self.__ip}:{self.__port}...')
        self.__listen()

    def __receive_message(self, client_socket) -> bool | dict[str, Any]:
        header_length = self.__header_length
        try:
            message_header = client_socket.recv(header_length)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def __listen(self):
        def handle_new_connection() -> bool:
            client_socket, client_address = self.__server_socket.accept()
            user = self.__receive_message(client_socket)
            if user is False:
                return False
            self.__sockets_list.append(client_socket)
            self.__clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user['data'].decode('utf-8')))
            return True

        def handle_existing_connection(socket) -> bool:
            message = self.__receive_message(socket)
            if message is False:
                print('Closed connection from: {}'.format(
                    self.__clients[socket]['data'].decode('utf-8')))
                self.__sockets_list.remove(socket)
                del self.__clients[socket]
                return False
            user = self.__clients[socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            for client_socket in self.__clients:
                if client_socket != socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
            return True

        def handle_exception_connection(socket):
            self.__sockets_list.remove(socket)
            del self.__clients[socket]

        while True:
            read_sockets, _, exception_sockets = select.select(self.__sockets_list, [], self.__sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self.__server_socket:
                    if not handle_new_connection():
                        continue
                else:
                    if not handle_existing_connection(notified_socket):
                        continue

            for notified_socket in exception_sockets:
                handle_exception_connection(notified_socket)


def get_config() -> Configuration:
    config_path: str = "../Config/config.ini"
    config = Configuration(config_path)
    return config


if __name__ == "__main__":
    config = get_config()
    server = Server(config)
    server.start()
