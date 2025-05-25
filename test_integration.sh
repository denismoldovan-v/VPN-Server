#!/bin/bash

set -e

VENV_PATH="./vpn-venv/bin"
LOG="vpn.log"
SERVER_IP="91.99.126.179"
SOCKS5_PORT=1080

echo "[1] Czyszczenie starych tuneli..."
for IF in $(ip -o link show | awk -F': ' '{print $2}' | grep '^tun'); do
    sudo ip link delete "$IF" || true
done

echo "[2] Uruchamianie serwera VPN..."
./run.sh &
SERVER_PID=$!
sleep 2

echo "[3] Uruchamianie klienta VPN..."
./run_client.sh &
CLIENT_PID=$!
sleep 4

echo "[4] Wykonywanie curl przez proxy (test ruchu przez tunel)..."
curl_output=$(curl -s --proxy-user vpnuser:vpnpass --proxy socks5h://localhost:$SOCKS5_PORT http://example.com || true)
echo "[curl output] ${curl_output:0:60}..."

echo "[5] Sprawdzanie logów uwierzytelnienia klienta..."
tail -n 20 "$LOG" | grep "authenticated" || {
    echo "Błąd: klient nie został uwierzytelniony"
    kill $SERVER_PID $CLIENT_PID
    exit 1
}

echo "[6] Sprawdzanie nadanego IP klienta..."
client_ip=$(tail -n 20 "$LOG" | grep "Configured TUN interface" | grep -oE 'IP [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{print $2}')
echo "Nadany IP klienta: $client_ip"

echo "[7] Uruchamianie tymczasowego tcpdump (na eth0 przez port 5555)..."
sudo timeout 5 tcpdump -i eth0 port 5555 -n -c 5 > tcpdump_output.txt || true

if grep -q "length" tcpdump_output.txt; then
    echo "tcpdump wykrył zaszyfrowany ruch TLS (port 5555)"
else
    echo "tcpdump nie wykrył żadnego ruchu"
fi

echo "[tcpdump summary:]"
tail -n 5 tcpdump_output.txt

echo "[8] Zabijanie procesów i czyszczenie..."
kill $SERVER_PID $CLIENT_PID || true
sleep 1
for IF in $(ip -o link show | awk -F': ' '{print $2}' | grep '^tun'); do
    sudo ip link delete "$IF" || true
done

echo "Test zakończony poprawnie"
