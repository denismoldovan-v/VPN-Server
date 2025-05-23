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
from tun_interface import create_tun_interface, configure_interface
from socks5_proxy import start_socks5_proxy


logger = setup_logger(config["log_file"])
logger.info("VPN server started.")

private_key = load_private_key(config["private_key_path"])
public_key = load_public_key(config["public_key_path"])

tun_fd = create_tun_interface(config["tun_interface"])
configure_interface(config["tun_interface"], config["tun_ip"], config["tun_netmask"])

threading.Thread(target=start_socks5_proxy, args=(config["socks5_port"],), daemon=True).start()
