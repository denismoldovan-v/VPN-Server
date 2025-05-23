# 🛡️ Custom VPN Server using TUN and SOCKS5 Proxy

A modular, Python-based VPN server that combines native Linux TUN interfaces with a built-in SOCKS5 proxy.  
Ideal for learning, experimentation, and lightweight TCP tunneling without heavyweight dependencies like OpenVPN or WireGuard.

Built to:
- Expose a local TUN device (e.g. tun0)
- Route traffic from SOCKS5 clients through the virtual interface
- Provide a clear, extensible structure for secure networking tools

## ✨ Features

- TUN interface creation and configuration via /dev/net/tun
- SOCKS5 proxy server for TCP traffic tunneling
- RSA key pair generation and loading (PEM format)
- Config-driven architecture via config.json
- Centralized logging to a rotating file
- Fully modular Python codebase, easy to extend

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
