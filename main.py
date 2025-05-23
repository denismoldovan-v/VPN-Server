"""
Main entry point for the custom VPN server.

This script initializes all major components:
- Sets up the TUN interface
- Starts the SOCKS5 proxy
- Initializes logging and configuration
- Manages the lifecycle of the VPN service
"""

import json
import threading
import time

from logger import setup_logger
from crypto_utils import load_private_key, load_public_key
from tun_interface import create_tun_interface, configure_interface
from socks5_proxy import start_socks5_proxy

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Setup logger
logger = setup_logger(config["log_file"])
logger.info("VPN server starting...")

# Load keys
try:
    private_key = load_private_key(config["private_key_path"])
    public_key = load_public_key(config["public_key_path"])
    logger.info("RSA key pair loaded successfully.")
except Exception as e:
    logger.error(f"Error loading keys: {e}")
    exit(1)

# Setup TUN interface
try:
    tun_fd = create_tun_interface(config["tun_interface"])
    configure_interface(config["tun_interface"], config["tun_ip"], config["tun_netmask"])
    logger.info(f"TUN interface {config['tun_interface']} configured.")
except Exception as e:
    logger.error(f"Error configuring TUN interface: {e}")
    exit(1)

# Start SOCKS5 proxy
try:
    threading.Thread(target=start_socks5_proxy, args=(config["socks5_port"],), daemon=True).start()
    logger.info(f"SOCKS5 proxy started on port {config['socks5_port']}")
except Exception as e:
    logger.error(f"Error starting SOCKS5 proxy: {e}")
    exit(1)

# Keep main thread alive
logger.info("VPN server is running.")
while True:
    time.sleep(60)
