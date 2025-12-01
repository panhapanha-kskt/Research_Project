from cryptography.fernet import Fernet

# Generate or load a key
def load_key():
    try:
        with open("secret.key", "rb") as file:
            key = file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as file:
            file.write(key)
    return key


key = load_key()
fernet = Fernet(key)


def encrypt_text(plaintext: str) -> str:
    """Encrypt a plaintext string using Fernet."""
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_text(ciphertext: str) -> str:
    """Decrypt ciphertext string using Fernet."""
    return fernet.decrypt(ciphertext.encode()).decode()
