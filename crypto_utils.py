"""
Utility functions for cryptographic operations.

Includes:
- RSA key generation
- Loading and saving private/public keys
- Optional encryption/decryption helpers
"""

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def generate_key_pair(private_path: str, public_path: str, key_size: int = 2048) -> None:
    key = RSA.generate(key_size)

    with open(private_path, 'wb') as priv_file:
        priv_file.write(key.export_key())

    with open(public_path, 'wb') as pub_file:
        pub_file.write(key.publickey().export_key())

def load_private_key(path: str) -> RSA.RsaKey:
    with open(path, 'rb') as f:
        return RSA.import_key(f.read())

def load_public_key(path: str) -> RSA.RsaKey:
    with open(path, 'rb') as f:
        return RSA.import_key(f.read())

def sign_with_private_key(data: bytes, private_key) -> bytes:
    h = SHA256.new(data)
    signature = pkcs1_15.new(private_key).sign(h)
    return signature

def verify_signature(data: bytes, signature: bytes, public_key) -> bool:
    h = SHA256.new(data)
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

