import socket
import threading
import os
import time
from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_private_key, sign_with_private_key

SERVER_IP = "91.99.126.179"  
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
    private_key = load_private_key("keys/private.pem")  # Twój klucz prywatny klienta

    # Odbierz nonce od serwera
    nonce = sock.recv(32)
    # Podpisz nonce
    signature = sign_with_private_key(nonce, private_key)
    # Wyślij podpis z powrotem
    sock.sendall(signature)

def main():
    # Łączymy się z serwerem
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    # Uwierzytelnianie
    authenticate_with_server(sock)

    client_ip = socket.inet_ntoa(sock.recv(4))
    server_ip = socket.inet_ntoa(sock.recv(4))

    tun_name = f"tun{os.getpid() % 1000}{int(time.time()) % 1000}"

    tun_fd = create_tun_interface(tun_name)
    configure_interface(tun_name, client_ip, "255.255.255.0")

    print(f"[VPN CLIENT] Configured TUN interface: {tun_name} with IP {client_ip}, server peer: {server_ip}")

    # Przepychamy pakiety
    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, sock)).start()
    threading.Thread(target=forward_socket_to_tun, args=(sock, tun_fd)).start()

if __name__ == "__main__":
    main()
