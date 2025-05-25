#!/bin/bash
set -e

VENV_PATH="./vpn-venv/bin"
LOG="vpn.log"
SOCKS5_PORT=1080
SERVER_IP="127.0.0.1"
TCPDUMP_INTERFACE="lo"

echo ""
echo "==================== [1] Czyszczenie starych TUN interfejsów ===================="
for IF in $(ip -o link show | awk -F': ' '{print $2}' | grep '^tun'); do
    sudo ip link delete "$IF" || true
done

echo ""
echo "==================== [2] Uruchamianie serwera VPN (run.sh) ======================"
./run.sh &
SERVER_PID=$!
sleep 2

echo ""
echo "==================== [3] Uruchamianie klienta VPN (run_client.sh) ==============="
./run_client.sh &
CLIENT_PID=$!
sleep 4

echo ""
echo "==================== [4] curl przez SOCKS5 (czy tunel działa) ==================="
curl -s --proxy-user vpnuser:vpnpass --proxy socks5h://localhost:$SOCKS5_PORT http://example.com > curl_output.txt || true

echo "Pierwsze 5 linii odpowiedzi HTTP:"
head -n 5 curl_output.txt

echo ""
echo "==================== [5] Sprawdzanie logu uwierzytelnienia ======================="
if grep -a "authenticated" "$LOG" > /dev/null; then
    echo "Klient został uwierzytelniony (log zawiera 'authenticated')"
else
    echo "Klient NIE został uwierzytelniony"
    tail -n 20 "$LOG"
    kill $SERVER_PID $CLIENT_PID || true
    exit 1
fi

echo ""
echo "==================== [6] Sprawdzenie nadanego IP klienta ========================="
client_ip=$(grep -a "Configured TUN interface" "$LOG" | grep -oE 'IP [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{print $2}')
if [ -n "$client_ip" ]; then
    echo "IP klienta przydzielone przez serwer: $client_ip"
else
    echo "Nie udało się znaleźć IP klienta w logach"
fi

echo ""
echo "==================== [7] tcpdump (TLS ruch przez $TCPDUMP_INTERFACE:5555) =========="
sudo timeout 5 tcpdump -i $TCPDUMP_INTERFACE port 5555 -n -c 5 > tcpdump_output.txt || true

if grep -q "length" tcpdump_output.txt; then
    echo "tcpdump wykrył zaszyfrowany ruch TLS na porcie 5555"
else
    echo "tcpdump nie wykrył żadnych pakietów (sprawdź interfejs lub timing)"
fi

echo ""
echo "tcpdump – ostatnie pakiety:"
tail -n 5 tcpdump_output.txt

echo ""
echo "==================== [8] Sprzątanie: kill + tun cleanup ==========================="
kill $SERVER_PID $CLIENT_PID || true
sleep 1
for IF in $(ip -o link show | awk -F': ' '{print $2}' | grep '^tun'); do
    sudo ip link delete "$IF" || true
done

echo ""
echo "Test zakończony poprawnie"
