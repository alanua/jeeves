cd /home/openclaw/jeeves

echo "==== 1. Deploy ===="
git pull
docker compose up -d --force-recreate api

echo "==== Waiting for API ===="
sleep 10

echo "==== 2. /health Verification ===="
curl -s http://localhost:8000/health < /dev/null
echo ""

echo "==== 3. /ask Verification ===="
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"Summarize the latest research on transformers","allow_tools":false}' < /dev/null
echo ""
