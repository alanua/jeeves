cd /home/openclaw/jeeves

echo "Raw alembic output (fixed):"
docker compose exec -T api alembic upgrade head < /dev/null || true

echo "Raw /health output:"
curl -s http://localhost:8000/health < /dev/null || true
echo ""

echo "Raw /ask output:"
API_KEY=$(cat .env | grep '^API_KEY=' | cut -d '=' -f 2)
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d '{"message":"What is the capital of Germany?","allow_tools":false}' < /dev/null || true
echo ""

echo "==== 11. Logs ===="
docker compose logs --tail=10 postgres < /dev/null || true
docker compose logs --tail=10 api < /dev/null || true
