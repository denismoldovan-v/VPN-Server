"""
Implements a minimal SOCKS5 proxy server.

Receives client connections and:
- Parses the SOCKS5 handshake
- Establishes TCP connections through the VPN tunnel
- Forwards traffic between client and target servers
"""
