#!/bin/bash

VENV_DIR="./vpn-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Tworzenie środowiska venv w $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "Uruchamianie klienta VPN..."
sudo env "PATH=$(realpath $VENV_DIR)/bin:$PATH" python3 tun_client.py
