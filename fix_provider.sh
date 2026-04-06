cd /home/openclaw/jeeves

echo "==== 1. Deploy ===="
git pull
docker compose up -d --force-recreate api

echo "==== Waiting for API ===="
sleep 10

echo "==== 2. Container ENV ===="
docker compose exec -T api /bin/sh -lc 'env | grep -E "OPENROUTER|OLLAMA|DEFAULT_MODE|ENABLE_CLOUD_FALLBACK|MOCK_PROVIDER_ENABLED" | sort' < /dev/null

echo "==== 3. /health Verification ===="
curl -s http://localhost:8000/health < /dev/null
echo ""

echo "==== 4. Localhost /ask Verification ===="
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}' < /dev/null
echo ""

echo "==== 5. Tailnet /ask Verification ===="
curl -s -X POST https://openclaw-server.taild84993.ts.net/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}' < /dev/null
echo ""
