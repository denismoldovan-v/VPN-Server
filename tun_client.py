import socket
import ssl
import threading
import os
import time

from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_private_key, sign_with_private_key
from logger import setup_logger

logger = setup_logger("vpn.log")

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
    private_key = load_private_key("keys/private.pem")

    nonce = sock.recv(32)
    signature = sign_with_private_key(nonce, private_key)
    sock.sendall(signature)

def main():
    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(cafile="tls/cert.pem")
        context.check_hostname = False
        sock = context.wrap_socket(raw_sock, server_hostname=SERVER_IP)
        sock.connect((SERVER_IP, SERVER_PORT))
        logger.info("[VPN CLIENT] Connected to server with TLS")
    except Exception as e:
        logger.error(f"[VPN CLIENT] TLS connection failed: {e}")
        return

    authenticate_with_server(sock)

    client_ip = socket.inet_ntoa(sock.recv(4))
    server_ip = socket.inet_ntoa(sock.recv(4))

    tun_name = f"tun{os.getpid() % 1000}{int(time.time()) % 1000}"
    tun_fd = create_tun_interface(tun_name)
    configure_interface(tun_name, client_ip, "255.255.255.0")

    logger.info(f"[VPN CLIENT] Configured TUN interface: {tun_name} with IP {client_ip}, server peer: {server_ip}")

    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, sock)).start()
    threading.Thread(target=forward_socket_to_tun, args=(sock, tun_fd)).start()

if __name__ == "__main__":
    main()
