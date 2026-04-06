cd /home/openclaw/jeeves

echo "==== 1. Deploy ===="
docker compose down
git pull
docker compose config
docker compose up --build -d

echo "==== Waiting for API ===="
sleep 15

echo "==== 2. Localhost Verification ===="
curl -s http://127.0.0.1:8000/health
echo ""

echo "==== 4. Tailscale Status ===="
tailscale status
echo ""

echo "==== 5. Tailscale Serve Status ===="
tailscale serve --bg 8000
tailscale serve status
echo ""

# Extract the URL from serve status (stripping color codes if any)
TS_URL=$(tailscale serve status | grep -o "https://[^ ]*" | head -1 | sed "s/\x1B\[[0-9;]*[a-zA-Z]//g")

# If empty, maybe it's serving HTTP
if [ -z "$TS_URL" ]; then
    TS_URL=$(tailscale serve status | grep -o "http://[^ ]*" | head -1 | sed "s/\x1B\[[0-9;]*[a-zA-Z]//g")
fi

echo "==== 7. Tailnet /health ===="
curl -s -k "$TS_URL/health"
echo ""

echo "==== 8. Tailnet /ask ===="
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -k -X POST "$TS_URL/ask" -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}'
echo ""

echo "==== 9. Logs ===="
docker compose logs --tail=100 api
