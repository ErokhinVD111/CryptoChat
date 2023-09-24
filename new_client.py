import asyncio
import socket
from configuration import Configuration, get_config

def input_user():
    username = input("Username: ")
    return username

class Client:
    def __init__(self, config: Configuration):
        self._reader_task = None
        self._server_ip: str = config.server["ip"]
        self._server_port: int = int(config.server["port"])
        self._header_length: int = int(config.message["header_length"])
        self._user_name: str = input_user()

    async def send_message(self, message: str):
        # Отправка сообщения асинхронно
        enc_message = message.encode('utf-8')
        message_header: bytes = f"{len(enc_message):<{self._header_length}}".encode('utf-8')
        if message:
            self._client_socket[1].write(message_header + enc_message)
            await self._client_socket[1].drain()

    async def connect(self):
        self._client_socket = await asyncio.open_connection(self._server_ip, self._server_port)
        await self._send_self_username()
        self._reader_task = asyncio.create_task(self._read_messages())
        await self._begin_chat()

    async def _send_self_username(self):
        enc_username: bytes = self._user_name.encode('utf-8')
        enc_header_username: bytes = f"{len(enc_username):<{self._header_length}}".encode('utf-8')
        self._client_socket[1].write(enc_header_username + enc_username)
        await self._client_socket[1].drain()

    async def _read_messages(self):
        while True:
            try:
                username_header: bytes = await self._client_socket[0].readexactly(self._header_length)
                if not len(username_header):
                    print('Connection closed by the server')
                    break

                username_length = int(username_header.decode('utf-8').strip())
                username = (await self._client_socket[0].readexactly(username_length)).decode('utf-8')
                message_header = await self._client_socket[0].readexactly(self._header_length)
                message_length = int(message_header.decode('utf-8').strip())
                message = (await self._client_socket[0].readexactly(message_length)).decode('utf-8')
                print(f'{username} > {message}')

            except Exception as e:
                print('Error reading message: ', str(e))
                break

    async def _begin_chat(self):
        while True:
            try:
                new_message = await asyncio.to_thread(input, f'{self._user_name} > ')
                await self.send_message(new_message)
            except KeyboardInterrupt:
                print('Exiting...')
                break

async def main():
    config: Configuration = get_config()
    client = Client(config)
    await client.connect()

if __name__ == '__main__':
    asyncio.run(main())
