cd /home/openclaw/jeeves

echo "==== 1. Deploy ===="
docker compose down -v
git pull
docker compose up --build -d

echo "==== Waiting for API ===="
sleep 10

echo "==== 2. Docker Compose PS ===="
docker compose ps

echo "==== 3. Localhost health Verification ===="
curl -s http://localhost:8000/health
echo ""
