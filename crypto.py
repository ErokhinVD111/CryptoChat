from cryptography.fernet import Fernet


def generate_symmetric_cipher() -> Fernet:
    key = Fernet.generate_key()
    cipher = Fernet(key)
    return cipher


