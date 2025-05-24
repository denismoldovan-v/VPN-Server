import socket
import threading
import os
import secrets

from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_public_key, verify_signature

SERVER_PORT = 5555
CLIENT_PUBKEY_PATH = "keys/public.pem"  # nowy plik z kluczem publicznym klienta

def forward_tun_to_socket(tun_fd, client_sock):
    while True:
        packet = os.read(tun_fd, 2048)
        client_sock.sendall(packet)

def forward_socket_to_tun(client_sock, tun_fd):
    while True:
        packet = client_sock.recv(2048)
        if not packet:
            break
        os.write(tun_fd, packet)

def authenticate_client(sock) -> bool:
    # Załaduj klucz publiczny klienta
    client_pubkey = load_public_key(CLIENT_PUBKEY_PATH)

    # Wygeneruj nonce
    nonce = secrets.token_bytes(32)
    sock.sendall(nonce)

    # Odbierz podpis od klienta
    signature = sock.recv(256)  # 2048-bitowy klucz RSA → 256 bajtów

    # Zweryfikuj podpis
    return verify_signature(nonce, signature, client_pubkey)

def main():
    tun_fd = create_tun_interface("tun0")
    configure_interface("tun0", "10.0.0.1", "255.255.255.0")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", SERVER_PORT))
    server_sock.listen(1)
    print(f"[VPN SERVER] Listening on port {SERVER_PORT}...")

    client_sock, addr = server_sock.accept()
    print(f"[VPN SERVER] Client connected from {addr}")

    if not authenticate_client(client_sock):
        print("[VPN SERVER] Client authentication failed. Closing connection.")
        client_sock.close()
        return
    print("[VPN SERVER] Client authenticated successfully.")

    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, client_sock)).start()
    threading.Thread(target=forward_socket_to_tun, args=(client_sock, tun_fd)).start()

if __name__ == "__main__":
    main()
