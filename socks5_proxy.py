"""
Implements a minimal SOCKS5 proxy server.

Receives client connections and:
- Parses the SOCKS5 handshake
- Establishes TCP connections through the VPN tunnel
- Forwards traffic between client and target servers
"""

import socket
import threading
import struct
import json

from logger import setup_logger

logger = setup_logger("vpn.log")

# Wczytaj dane z config.json
with open("config.json", "r") as f:
    config = json.load(f)

USERNAME = config.get("socks5_username", "")
PASSWORD = config.get("socks5_password", "")

def handle_client(client_socket):
    # SOCKS5 handshake
    data = client_socket.recv(2)
    if len(data) < 2:
        client_socket.close()
        return

    ver, nmethods = struct.unpack("!BB", data)
    methods = client_socket.recv(nmethods)

    if 0x02 not in methods:
        client_socket.sendall(b"\x05\xFF")  # brak wspólnej metody
        client_socket.close()
        return

    client_socket.sendall(b"\x05\x02")  # wybieramy Username/Password

    # Autoryzacja RFC1929
    auth_ver = client_socket.recv(1)
    if auth_ver != b"\x01":
        client_socket.close()
        return

    ulen = client_socket.recv(1)[0]
    uname = client_socket.recv(ulen).decode()

    plen = client_socket.recv(1)[0]
    passwd = client_socket.recv(plen).decode()

    if uname != USERNAME or passwd != PASSWORD:
        client_socket.sendall(b"\x01\x01")  # auth failed
        client_socket.close()
        return

    client_socket.sendall(b"\x01\x00")  # auth success

    # Request header
    header = client_socket.recv(4)
    if len(header) < 4:
        client_socket.close()
        return

    ver, cmd, _, atype = struct.unpack("!BBBB", header)

    if atype == 1:  # IPv4
        addr = socket.inet_ntoa(client_socket.recv(4))
    elif atype == 3:  # Domain name
        domain_len = client_socket.recv(1)[0]
        addr = client_socket.recv(domain_len).decode()
    elif atype == 4:  # IPv6
        addr = socket.inet_ntop(socket.AF_INET6, client_socket.recv(16))
    else:
        client_socket.close()
        return

    port = struct.unpack('!H', client_socket.recv(2))[0]

    # Connect to destination
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote.connect((addr, port))
        client_socket.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack("!H", 0))
    except:
        client_socket.close()
        return

    def relay(src, dst):
        while True:
            try:
                data = src.recv(4096)
                if not data:
                    break
                logger.info(f"[SOCKS5] Relaying {len(data)} bytes")
                dst.sendall(data)
            except Exception as e:
                logger.warning(f"[SOCKS5] Relay error: {e}")
                break


    threading.Thread(target=relay, args=(client_socket, remote)).start()
    threading.Thread(target=relay, args=(remote, client_socket)).start()

def start_socks5_proxy(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    logger.info(f"[SOCKS5] Listening on port {port}")

    while True:
        client, _ = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()
