import socket
import threading
import os
from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_private_key, sign_with_private_key

SERVER_IP = "91.99.126.179"  # ← ZMIEŃ na IP Twojego serwera
SERVER_PORT = 5555

def forward_tun_to_socket(tun_fd, sock):
    while True:
        packet = os.read(tun_fd, 2048)
        sock.sendall(packet)

def forward_socket_to_tun(sock, tun_fd):
    while True:
        packet = sock.recv(2048)
        if not packet:
            break
        os.write(tun_fd, packet)

def authenticate_with_server(sock):
    private_key = load_private_key("keys/client_private.pem")  # Twój klucz prywatny klienta

    # Odbierz nonce od serwera
    nonce = sock.recv(32)
    # Podpisz nonce
    signature = sign_with_private_key(nonce, private_key)
    # Wyślij podpis z powrotem
    sock.sendall(signature)

def main():
    # Tworzymy interfejs TUN
    tun_fd = create_tun_interface("tun0")
    configure_interface("tun0", "10.0.0.2", "255.255.255.0")  # ← adres klienta

    # Łączymy się z serwerem
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    # Uwierzytelnianie
    authenticate_with_server(sock)

    # Przepychamy pakiety
    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, sock)).start()
    threading.Thread(target=forward_socket_to_tun, args=(sock, tun_fd)).start()

if __name__ == "__main__":
    main()
