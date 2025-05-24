#!/bin/bash

VENV_DIR="./vpn-venv"  

if [ ! -d "$VENV_DIR" ]; then
    echo "Tworzenie środowiska venv w $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

if [ -f requirements.txt ]; then
    echo "Instalacja pakietów z requirements.txt"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r requirements.txt
else
    echo "Brak pliku requirements.txt"
    exit 1
fi


echo "Uruchamianie serwera VPN..."
sudo env "PATH=$(realpath $VENV_DIR)/bin:$PATH" python main.py
