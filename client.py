import asyncio
import socket
import errno
import sys

from configuration import Configuration, get_config


def input_user():
    username = input("Username: ")
    return username


class Client:
    def __init__(self, config: Configuration):
        self._server_ip: str = config.server["ip"]
        self._server_port: int = int(config.server["port"])
        self._header_length: int = int(config.message["header_length"])
        self._user_name: str = input_user()
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, message: str) -> bool:
        message_header: str = f"{len(message):<{self._header_length}}"
        final_message = message_header + message
        if message:
            encoded_message = final_message.encode('utf-8')
            self._client_socket.send(encoded_message)
            return True
        return False

    def _send_self_username(self):
        username_header: str = f"{len(self._user_name):<{self._header_length}}"
        self._client_socket.send((username_header + self._user_name).encode("utf-8"))

    def connect(self):
        self._client_socket.connect((self._server_ip, self._server_port))
        self._client_socket.setblocking(False)
        self._send_self_username()
        self._begin_chat()

    def _receive_message(self):
        while True:
            username_header = self._client_socket.recv(self._header_length)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())
            username = self._client_socket.recv(username_length).decode('utf-8')

            message_header = self._client_socket.recv(self._header_length)
            message_length = int(message_header.decode('utf-8').strip())
            message = self._client_socket.recv(message_length).decode('utf-8')

            print(f'{username} > {message}')

    async def _begin_chat(self):
        def create_new_message():
            new_message: str = input(f'{self._user_name} > ')
            if new_message:
                return new_message
            return ""

        while True:
            try:
                new_message = create_new_message()
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


async def main():
    config: Configuration = get_config()
    client = Client(config)
    client.connect()


if __name__ == '__main__':
    asyncio.run(main())
