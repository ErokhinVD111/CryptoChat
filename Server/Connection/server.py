import socket
import select
from Config.ConfigurationLoader import ConfigurationLoader


class Server:
    def __init__(self, config: ConfigurationLoader):
        self.__clients = None
        self.__sockets_list = None
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_ - socket option
        # SOL_ - socket option level
        # Sets REUSEADDR (as a socket option) to 1 on socket
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind, so server informs operating system that it's going to use given IP and port For a server using 0.0.0.0 means
        # to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
        self.__ip = config.server["ip"]
        self.__port = int(config.server["port"])

        self.__server_socket.bind((self.__ip, self.__port))

    def start(self):
        # This makes server listen to new connections
        self.__server_socket.listen()

        # List of sockets for select.select()
        self.__sockets_list = [self.__server_socket]

        # List of connected clients - socket as a key, user header and name as data
        self.__clients = {}

        print(f'Listening for connections on {self.__ip}:{self.__port}...')


def get_config() -> ConfigurationLoader:
    config_path: str = "../../Config/config.ini"
    config = ConfigurationLoader(config_path)
    return config


if __name__ == "__main__":
    config = get_config()
    server = Server(config)
    server.start()

