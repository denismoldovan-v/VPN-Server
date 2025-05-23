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

def handle_client(client_socket):
    # SOCKS5 handshake (version, methods)
    client_socket.recv(2)         # Version + nmethods
    client_socket.recv(1)         # Methods (we ignore and accept all)
    client_socket.sendall(b"\x05\x00")  # Accept "no auth"

    # Request header
    ver, cmd, _, atype = struct.unpack("!BBBB", client_socket.recv(4))
    
    if atype == 1:  # IPv4
        addr = socket.inet_ntoa(client_socket.recv(4))
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

    # Relay
    def relay(src, dst):
        while True:
            try:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
            except:
                break

    threading.Thread(target=relay, args=(client_socket, remote)).start()
    threading.Thread(target=relay, args=(remote, client_socket)).start()

def start_socks5_proxy(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[SOCKS5] Listening on port {port}")

    while True:
        client, _ = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()
