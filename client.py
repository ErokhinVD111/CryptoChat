import asyncio
import socket
import errno
import sys
from asyncio import StreamReader, StreamWriter

from configuration import Configuration, get_config


def input_user():
    username = input("Username: ")
    return username


class Client:
    def __init__(self, config: Configuration):
        self._socket_writer = None
        self._socket_reader = None
        self._server_ip: str = config.server["ip"]
        self._server_port: int = int(config.server["port"])
        self._header_length: int = int(config.message["header_length"])
        self._user_name: str = input_user()

    def send_message(self, message: str) -> bool:
        enc_message = message.encode('utf-8')
        message_header: bytes = f"{len(enc_message):<{self._header_length}}".encode('utf-8')
        if message:
            self._socket_writer.write(message_header + enc_message)
            return True
        return False

    def _send_self_username(self):
        enc_username: bytes = self._user_name.encode('utf-8')
        enc_header_username: bytes = f"{len(enc_username):<{self._header_length}}".encode('utf-8')
        self._client_socket.send(enc_header_username + enc_username)

    def connect(self):
        self._socket_reader, self._socket_writer = await asyncio.open_connection(self._server_ip, self._server_port)
        await self._send_self_username()
        await self._begin_chat()
        await self._receive_message()
        self._send_self_username()
        self._begin_chat()

    def _receive_message(self):

        def decode_message(username_header: bytes):
            username_length = int(username_header.decode('utf-8').strip())
            username = self._client_socket.recv(username_length).decode('utf-8')
            message_header = self._client_socket.recv(self._header_length)
            message_length = int(message_header.decode('utf-8').strip())
            message = self._client_socket.recv(message_length).decode('utf-8')
            print(f'{username} > {message}')

        while True:
            username_header: bytes = self._client_socket.recv(self._header_length)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            decode_message(username_header)

    def _begin_chat(self):
        while True:
            try:
                new_message = input(f'{self._user_name} > ')
                self.send_message(new_message)
                self._receive_message()

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()


if __name__ == '__main__':
    config: Configuration = get_config()
    client = Client(config)
    client.connect()
