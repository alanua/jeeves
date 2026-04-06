cd /home/openclaw/jeeves

echo "==== 1. Deploy ===="
docker compose down -v
git pull
docker compose up --build -d

echo "==== Waiting for API ===="
sleep 15

echo "==== 2. Alembic Exec ===="
docker compose exec -T api alembic upgrade head < /dev/null

echo "==== 3. /health Verification ===="
curl -s http://localhost:8000/health < /dev/null
echo ""

echo "==== 4. /ask Verification ===="
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}' < /dev/null
echo ""

echo "==== 5. Logs (if failed) ===="
docker compose logs --tail=100 api < /dev/null
