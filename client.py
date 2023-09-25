import asyncio
import errno
import sys

from configuration import Configuration, get_config
from crypto_tools import CryptoTools


def input_user():
    username = input('Username:')
    return username


class Client:
    def __init__(self, config: Configuration):
        self._stream_writer = None
        self._stream_reader = None
        self._server_ip: str = config.server["ip"]
        self._server_port: int = int(config.server["port"])
        self._header_length: int = int(config.message["header_length"])
        self._username: str = ""
        self._crypto_tools: CryptoTools = CryptoTools()
        self._socket = None

    async def _send_message(self):
        while True:
            new_message = await asyncio.to_thread(input)
            enc_message = new_message.encode('utf-8')
            enc_message_header: bytes = f"{len(enc_message):<{self._header_length}}".encode('utf-8')
            if new_message:
                message_for_encryption = enc_message_header + enc_message
                encrypted_message = self._crypto_tools.encrypt_message(self._socket, message_for_encryption)
                self._stream_writer.write(f"{len(encrypted_message):<{self._header_length}}".encode('utf-8') + encrypted_message)
                await self._stream_writer.drain()

    async def _send_self_username(self):
        enc_username: bytes = self._username.encode('utf-8')
        enc_username_header: bytes = f"{len(enc_username):<{self._header_length}}".encode('utf-8')
        message_for_encryption = enc_username_header + enc_username
        # encrypted_message = self._crypto_tools.encrypt_message(self._socket, message_for_encryption)
        self._stream_writer.write(message_for_encryption)
        await self._stream_writer.drain()

    async def connect(self):
        self._stream_reader, self._stream_writer = await asyncio.open_connection(self._server_ip, self._server_port)
        self._socket = self._stream_writer.get_extra_info('sockname')  # Получаем адрес клиента
        print(self._socket)
        await self._begin_chat()

    async def _receive_messages(self):
        async def decode_message(decrypted_message: bytes):
            username_length = int(username_header.decode('utf-8').strip())
            username = (await self._stream_reader.readexactly(username_length)).decode('utf-8')
            message_header = await self._stream_reader.readexactly(self._header_length)
            message_length = int(message_header.decode('utf-8').strip())
            message = (await self._stream_reader.readexactly(message_length)).decode('utf-8')
            print(f'{username} > {message}')

        while True:
            try:
                encrypted_header: bytes = await self._stream_reader.readexactly(self._header_length)
                encrypted_message_length = int(encrypted_header.decode('utf-8').strip())
                encrypted_message = await self._stream_reader.readexactly(encrypted_message_length)
                decrypted_message = self._crypto_tools.decrypt_message(self._socket, encrypted_message)

                username_header: bytes = decrypted_message[:self._header_length]
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = decrypted_message[self._header_length: self._header_length + username_length]
                message_header = decrypted_message[
                                 self._header_length + username_length: self._header_length + username_length + self._header_length]
                message_length = int(message_header.decode('utf-8').strip())
                message = decrypted_message[
                          self._header_length + username_length + self._header_length: self._header_length + username_length + self._header_length + message_length]

                print(f'{username} > {message}')
                # if not len(username_header):
                #     print('Connection closed by the server')
                #     sys.exit()
                #
                #
                #
                # await decode_message(username_header)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()

    async def _begin_chat(self):
        self._username: str = input_user()
        print('Welcome to chat:\n')
        await self._send_self_username()
        await asyncio.gather(self._send_message(), self._receive_messages())


async def main():
    config: Configuration = get_config()
    client = Client(config)
    await client.connect()


if __name__ == '__main__':
    asyncio.run(main())
