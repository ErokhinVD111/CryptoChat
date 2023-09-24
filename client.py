import asyncio
import errno
import sys
from aioconsole import ainput

from configuration import Configuration, get_config


async def input_user():
    username = await ainput('Username:')
    return username


class Client:
    def __init__(self, config: Configuration):
        self._socket_writer = None
        self._socket_reader = None
        self._server_ip: str = config.server["ip"]
        self._server_port: int = int(config.server["port"])
        self._header_length: int = int(config.message["header_length"])
        self._username: str = ""

    async def _send_message(self):
        while True:
            # new_message = await asyncio.to_thread(input, f'{self._user_name} > ')
            new_message = await ainput(f'{self._username} > ')
            enc_message = new_message.encode('utf-8')
            enc_message_header: bytes = f"{len(enc_message):<{self._header_length}}".encode('utf-8')
            if new_message:
                self._socket_writer.write(enc_message_header + enc_message)
                await self._socket_writer.drain()

    async def _send_self_username(self):
        enc_username: bytes = self._username.encode('utf-8')
        enc_username_header: bytes = f"{len(enc_username):<{self._header_length}}".encode('utf-8')
        self._socket_writer.write(enc_username_header + enc_username)
        await self._socket_writer.drain()

    async def connect(self):
        self._socket_reader, self._socket_writer = await asyncio.open_connection(self._server_ip, self._server_port)
        await self._begin_chat()

    async def _receive_messages(self):
        async def decode_message(username_header: bytes):
            username_length = int(username_header.decode('utf-8').strip())
            username = (await self._socket_reader.readexactly(username_length)).decode('utf-8')
            message_header = await self._socket_reader.readexactly(self._header_length)
            message_length = int(message_header.decode('utf-8').strip())
            message = (await self._socket_reader.readexactly(message_length)).decode('utf-8')
            print(f'{username} > {message}')

        while True:
            try:
                username_header: bytes = await self._socket_reader.readexactly(self._header_length)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                await decode_message(username_header)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()

    async def _begin_chat(self):
        self._username: str = await input_user()
        await self._send_self_username()
        await asyncio.gather(self._send_message(), self._receive_messages())
        # await asyncio.create_task(self._send_message())
        # await asyncio.create_task(self._receive_messages())
        # await self._receive_messages()
        # await self._send_message()


async def main():
    config: Configuration = get_config()
    client = Client(config)
    await client.connect()


if __name__ == '__main__':
    asyncio.run(main())
