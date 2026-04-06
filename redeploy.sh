cd /home/openclaw/jeeves
echo "==== Pulling & Redeploying ===="
docker compose down -v
git pull
docker compose up --build -d

echo "Waiting for API startup..."
sleep 10

echo "==== 10. Alembic Exec ===="
docker compose exec -T api alembic upgrade head < /dev/null

echo "==== 11. /health Endpoint ===="
curl -s http://localhost:8000/health < /dev/null
echo ""

echo "==== 12. /ask Endpoint ===="
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}' < /dev/null
echo ""

echo "==== 13. Logs ===="
docker compose logs --tail=100 api < /dev/null
docker compose logs --tail=100 postgres < /dev/null
