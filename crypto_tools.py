import base64

from cryptography.fernet import Fernet
from typing import Dict
from socket import socket as Socket
import json


class CryptoTools:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CryptoTools, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client_cipher = None

    def add_client(self, socket_info):
        key = Fernet.generate_key()
        with open(f'{socket_info}.json', 'w') as file_obj:
            base64_key = base64.b64encode(key).decode('utf-8')
            json.dump(json.dumps({f"{socket_info}": base64_key}), file_obj, indent=4)

    def encrypt_message(self, socket_info: tuple, message: bytes):
        self.client_cipher = {}
        with open(f"{socket_info}.json", 'r') as file_obj:
            json_str = json.load(file_obj)
            json_obj = json.loads(json_str)

        key = base64.b64decode(json_obj[f'{socket_info}'].encode('utf-8'))
        self.client_cipher[socket_info] = Fernet(key)
        return self.client_cipher[socket_info].encrypt(message)

    def decrypt_message(self, socket_info: tuple, message: bytes):
        self.client_cipher = {}
        with open(f"{socket_info}.json", 'r') as file_obj:
            json_str = json.load(file_obj)
            json_obj = json.loads(json_str)

        key = base64.b64decode(json_obj[f'{socket_info}'].encode('utf-8'))
        self.client_cipher[socket_info] = Fernet(key)
        return self.client_cipher[socket_info].decrypt(message)
