"""
Custom logging utility for the VPN service.

Handles:
- Logging connections, disconnections, and errors
- Writing timestamped entries to a log file
- Supporting multiple log levels (info, warning, error)
"""

import logging

def setup_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("vpn_logger")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)

    return logger
