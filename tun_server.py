import socket
import threading
import os
import secrets

from tun_interface import create_tun_interface, configure_interface
from crypto_utils import load_public_key, verify_signature

SERVER_PORT = 5555
CLIENT_PUBKEY_PATH = "keys/public.pem"

client_counter = 0
counter_lock = threading.Lock()

def forward_tun_to_socket(tun_fd, client_sock):
    while True:
        try:
            packet = os.read(tun_fd, 2048)
            client_sock.sendall(packet)
        except:
            break

def forward_socket_to_tun(client_sock, tun_fd):
    while True:
        try:
            packet = client_sock.recv(2048)
            if not packet:
                break
            os.write(tun_fd, packet)
        except:
            break

def authenticate_client(sock) -> bool:
    client_pubkey = load_public_key(CLIENT_PUBKEY_PATH)
    nonce = secrets.token_bytes(32)
    sock.sendall(nonce)
    signature = sock.recv(256)
    return verify_signature(nonce, signature, client_pubkey)

def handle_client(client_sock, addr):
    global client_counter

    print(f"[VPN SERVER] New connection from {addr}")
    if not authenticate_client(client_sock):
        print(f"[VPN SERVER] Client {addr} failed authentication.")
        client_sock.close()
        return
    print(f"[VPN SERVER] Client {addr} authenticated.")

    with counter_lock:
        tun_id = client_counter
        client_counter += 1

    tun_name = f"tun{tun_id + 1}"  # tun1, tun2, ...
    tun_ip = f"10.0.0.{tun_id + 1}"  # unikalny IP np. 10.0.0.2, 10.0.0.3 itd.

    tun_fd = create_tun_interface(tun_name)
    configure_interface(tun_name, tun_ip, "255.255.255.0")
    client_sock.sendall(socket.inet_aton(tun_ip))

    print(f"[VPN SERVER] TUN interface {tun_name} set up for {addr}")

    threading.Thread(target=forward_tun_to_socket, args=(tun_fd, client_sock), daemon=True).start()
    threading.Thread(target=forward_socket_to_tun, args=(client_sock, tun_fd), daemon=True).start()

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", SERVER_PORT))
    server_sock.listen(5)
    print(f"[VPN SERVER] Listening on port {SERVER_PORT}...")

    while True:
        client_sock, addr = server_sock.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()
