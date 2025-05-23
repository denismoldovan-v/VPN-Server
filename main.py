"""
Main entry point for the custom VPN server.

This script initializes all major components:
- Sets up the TUN interface
- Starts the SOCKS5 proxy
- Initializes logging and configuration
- Manages the lifecycle of the VPN service
"""

from logger import setup_logger
from crypto_utils import load_private_key, load_public_key

logger = setup_logger(config["log_file"])
logger.info("VPN server started.")
private_key = load_private_key(config["private_key_path"])
public_key = load_public_key(config["public_key_path"])
