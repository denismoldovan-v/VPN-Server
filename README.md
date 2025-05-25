# 🛡️ Custom VPN Server using TUN and SOCKS5 Proxy

A modular, Python-based VPN server that combines native Linux TUN interfaces with a built-in SOCKS5 proxy.  
Ideal for learning, experimentation, and lightweight TCP tunneling without heavyweight dependencies like OpenVPN or WireGuard.

Built to:
- Expose a local TUN device (e.g. tun0)
- Route traffic from SOCKS5 clients through the virtual interface
- Provide a clear, extensible structure for secure networking tools

## ✨ Features

- TUN interface creation and configuration via `/dev/net/tun`
- TLS encryption between client and server using RSA certificates
- Client authentication via signed nonce using RSA key pairs
- SOCKS5 proxy server for TCP traffic tunneling with username/password authentication (RFC 1929)
- IP-based rate limiting to protect against brute-force or DoS attacks
- Isolated TUN interfaces and unique IPs per client
- Centralized logging with timestamps to `vpn.log`
- Configurable architecture via `config.json`
- Modular Python codebase, easy to extend and adapt


## 🧰 Requirements

- Linux system with support for /dev/net/tun
- Python 3.8 or higher
- Root privileges to bring up the TUN interface
- OpenSSL (for manual key generation, optional)


## 📄 config.json

The `config.json` file contains customizable configuration settings for the VPN server.  
This allows the server to be easily reconfigured without changing the source code.

### 🔧 Example structure:

```json
{
  "tun_interface": "tun0",
  "tun_ip": "10.0.0.1",
  "tun_netmask": "255.255.255.0",
  "socks5_port": 1080,
  "log_file": "vpn.log",
  "private_key_path": "keys/private.pem",
  "public_key_path": "keys/public.pem"
}

```

## 🚀 Getting Started

1. Ensure you're running on a Linux system with /dev/net/tun available.
2. Create the `keys/` folder if it doesn't exist.
3. Generate RSA keys (once only):

   from crypto_utils import generate_key_pair  
   generate_key_pair("keys/private.pem", "keys/public.pem")

4. Launch the VPN server with root privileges:

   sudo python3 main.py

5. Connect any SOCKS5-compatible client (e.g. curl, Firefox, proxychains) to:  
   `localhost:1080`


## 🧱 Architecture

The VPN server consists of three main components working together:

1. **SOCKS5 Proxy Server**  
   Accepts TCP connections from SOCKS5-compatible clients and relays them to the destination.

2. **TUN Interface (`tun0`)**  
   A virtual network interface used to route and capture packets within the server's operating system.

3. **Main Controller (`main.py`)**  
   Initializes the system, sets up configuration, logging, TUN interface, and starts the SOCKS5 proxy.

Data flow:

Client (SOCKS5) → SOCKS5 Proxy → TUN Interface → Internet
                                ↑
                           RSA Keys & Logging



## 🔐 Security Considerations

This VPN server was built with practical security in mind. Below is an overview of implemented features and what remains to be addressed for full production hardening:

| Area                                | Status      | Description                                                                 |
|-------------------------------------|-------------|-----------------------------------------------------------------------------|
| TLS encryption                      | ✅ Done      | All communication between client and server is encrypted using TLS over port 5555. Self-signed certificates are used by default. |
| Client authentication (VPN layer)   | ✅ Done      | Clients must prove identity by signing a server-provided nonce with their RSA private key. |
| SOCKS5 authentication (proxy layer) | ✅ Done      | Username and password authentication implemented per RFC 1929.              |
| Rate limiting / DoS protection      | ✅ Done      | Per-IP connection attempts are rate-limited (e.g., 5 attempts per 60s). Clients exceeding the limit are temporarily blocked. |
| Isolated TUN interfaces             | ✅ Done      | Each client is assigned a unique TUN interface and private IP.              |
| Interface cleanup                   | ✅ Done      | TUN interfaces are deleted automatically when a client disconnects.         |
| Logging with timestamps             | ✅ Done      | All events (auth, errors, SOCKS5 relays) are logged to `vpn.log`.           |
| SOCKS5 proxy integration            | ✅ Done      | The proxy server is launched in a thread inside the main VPN process.       |
| TLS cert from CA (e.g. Let's Encrypt)| ❌ Not yet  | Current TLS certificates are self-signed. Use a CA-signed cert for production. |
| Packet filtering / firewall rules   | ❌ Not yet   | No filtering of traffic or destination IPs. Recommend `iptables` or `nftables`. |
| Persistent blacklisting             | ❌ Not yet   | Currently, rate-limited IPs are only temporarily blocked in-memory.         |
| Monitoring / restart strategy       | ❌ Not yet   | No external service monitor. Recommend `systemd`, `tmux`, or Docker.        |
| Log shipping / syslog integration   | ❌ Not yet   | Logs are local only. Recommend syslog or ELK stack for central logging.     |

### 🧠 Summary

The VPN ensures encrypted and authenticated access, with SOCKS5 login and connection throttling to prevent abuse. Further improvements like persistent IP banning, production-grade TLS certs, and firewall integration are recommended for full deployment.

