import socket
import threading
import os
from tun_interface import create_tun_interface, configure_interface

SERVER_PORT = 5555

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

def main():
    tun_fd = create_tun_interface("tun0")
    configure_interface("tun0", "10.0.0.1", "255.255.255.0")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", SERVER_PORT))
    server_sock.listen(1)
    print(f"[VPN SERVER] Listening on port {SERVER_PORT}...")

    client_sock, addr = server_sock.accept()
    print(f"[VPN SERVER] Client connected from {addr}")

    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, client_sock)).start()
    threading.Thread(target=forward_socket_to_tun, args=(client_sock, tun_fd)).start()

if __name__ == "__main__":
    main()
