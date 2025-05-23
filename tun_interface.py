"""
Handles creation and configuration of the TUN interface.

Provides functions to:
- Open /dev/net/tun
- Set IP address and bring the interface up
- Read and write raw packets to the virtual network device
"""

import os
import fcntl
import struct
import subprocess

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

def create_tun_interface(name: str) -> int:
    tun_fd = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", name.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
    return tun_fd

def configure_interface(name: str, ip: str, netmask: str):
    subprocess.run(["ip", "addr", "add", f"{ip}/24", "dev", name], check=True)
    subprocess.run(["ip", "link", "set", "dev", name, "up"], check=True)
