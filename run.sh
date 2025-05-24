#!/bin/bash

# Sprawdzenie czy python3 -m venv działa
python3 -m venv --help >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Brakuje python3-venv. Zainstaluj go komendą:"
    echo "    sudo apt install python3-venv"
    exit 1
fi

# Zabijanie poprzednich instancji main.py i tun_server.py
for pid in $(ps aux | grep -E 'main.py|tun_server.py' | grep -v grep | awk '{print $2}'); do
    echo "Zabijanie procesu PID $pid"
    sudo kill -9 $pid
done

# Usuwanie wszystkich interfejsów tun*
for IF in $(ip -o link show | awk -F': ' '{print $2}' | grep '^tun'); do
    echo "Usuwanie interfejsu $IF"
    sudo ip link delete "$IF"
done

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

echo "Uruchamianie serwera VPN (main.py + tun_server.py)..."
sudo env "PATH=$(realpath $VENV_DIR)/bin:$PATH" python3 main.py &
sudo env "PATH=$(realpath $VENV_DIR)/bin:$PATH" python3 tun_server.py
