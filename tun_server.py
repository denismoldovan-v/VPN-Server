import socket
import threading
import os
import secrets
import atexit
import subprocess
import signal
import sys

from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_public_key, verify_signature
from logger import setup_logger

logger = setup_logger("vpn.log")

#cleanup for previously created interfaces
created_interfaces = []

SERVER_TUN_IP = "10.8.0.1"

def delete_interfaces():
    for iface in created_interfaces:
        try:
            logger.info(f"[CLEANUP] Deleting interface {iface}")
            subprocess.run(["ip", "link", "delete", iface], check=True)
        except Exception as e:
            logger.warning(f"[CLEANUP ERROR] Could not delete {iface}: {e}")

atexit.register(delete_interfaces)

def handle_signal(sig, frame):
    logger.info("[SIGNAL] Caught termination signal.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

SERVER_PORT = 5555
CLIENT_PUBKEY_PATH = "keys/public.pem"

client_counter = 0
counter_lock = threading.Lock()

def cleanup_interface(name):
    try:
        logger.info(f"[CLEANUP] Deleting interface {name}")
        subprocess.run(["ip", "link", "delete", name], check=True)
    except Exception as e:
        logger.warning(f"[CLEANUP ERROR] Could not delete {name}: {e}")

def forward_tun_to_socket(tun_fd, client_sock, tun_name):
    try:
        while True:
            packet = os.read(tun_fd, 2048)
            client_sock.sendall(packet)
    except:
        pass
    finally:
        cleanup_interface(tun_name)

def forward_socket_to_tun(client_sock, tun_fd, tun_name):
    try:
        while True:
            packet = client_sock.recv(2048)
            if not packet:
                break
            os.write(tun_fd, packet)
    except:
        pass
    finally:
        cleanup_interface(tun_name)

def authenticate_client(sock) -> bool:
    client_pubkey = load_public_key(CLIENT_PUBKEY_PATH)
    nonce = secrets.token_bytes(32)
    sock.sendall(nonce)
    signature = sock.recv(256)
    return verify_signature(nonce, signature, client_pubkey)

def handle_client(client_sock, addr):
    global client_counter

    logger.info(f"[VPN SERVER] New connection from {addr}")
    if not authenticate_client(client_sock):
        logger.info(f"[VPN SERVER] Client {addr} failed authentication.")
        client_sock.close()
        return
    logger.info(f"[VPN SERVER] Client {addr} authenticated.")

    with counter_lock:
        tun_id = client_counter
        client_counter += 1

    tun_name = f"tun{tun_id + 1}"  # tun1, tun2, ...
    created_interfaces.append(tun_name)

    tun_ip = f"10.0.0.{tun_id + 1}"

    tun_fd = create_tun_interface(tun_name)

    client_ip = f"10.8.0.{tun_id + 2}"
    server_ip = SERVER_TUN_IP

    configure_interface(tun_name, server_ip, "255.255.255.0")

    # Wyślij oba IP do klienta
    client_sock.sendall(socket.inet_aton(client_ip))
    client_sock.sendall(socket.inet_aton(server_ip))

    logger.info(f"[VPN SERVER] TUN interface {tun_name} set up for {addr}")

    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, client_sock, tun_name), daemon=True).start()
    threading.Thread(target=forward_socket_to_tun, args=(client_sock, tun_fd, tun_name), daemon=True).start()

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_sock.bind(("0.0.0.0", SERVER_PORT))
    except OSError as e:
        logger.error(f"[ERROR] Cannot bind to port {SERVER_PORT}: {e}")
        exit(1)

    server_sock.listen(5)
    logger.info(f"[VPN SERVER] Listening on port {SERVER_PORT}...")

    while True:
        client_sock, addr = server_sock.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()
