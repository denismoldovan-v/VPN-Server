#!/bin/bash

VENV_DIR="$HOME/vpn-venv"

# Tworzenie środowiska virtualenv jeśli nie istnieje
if [ ! -d "$VENV_DIR" ]; then
    echo "Tworzenie środowiska venv w $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Aktywacja środowiska
source "$VENV_DIR/bin/activate"

# Instalacja zależności
if [ -f requirements.txt ]; then
    echo "Instalacja pakietów z requirements.txt"
    pip install -r requirements.txt
else
    echo "Brak pliku requirements.txt"
fi

# Uruchomienie aplikacji z uprawnieniami administratora
echo "Uruchamianie serwera VPN..."
sudo "$VENV_DIR/bin/python3" main.py
