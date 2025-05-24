#!/bin/bash

VENV_DIR="$HOME/vpn-venv"

# Tworzenie środowiska virtualenv jeśli nie istnieje
if [ ! -d "$VENV_DIR" ]; then
    echo "Tworzenie środowiska venv w $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Instalacja zależności bez aktywacji venv (bo i tak uruchamiamy z PATH)
if [ -f requirements.txt ]; then
    echo "Instalacja pakietów z requirements.txt"
    "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
    "$VENV_DIR/bin/pip" install -r requirements.txt
else
    echo "Brak pliku requirements.txt"
    exit 1
fi

# Uruchomienie aplikacji z uprawnieniami root i z venv w PATH
echo "Uruchamianie serwera VPN..."
sudo env "PATH=$VENV_DIR/bin:$PATH" python main.py
