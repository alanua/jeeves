cd /home/openclaw/jeeves
echo "==== OPENROUTER config ===="
grep OPENROUTER .env
echo "==== API LOGS ===="
docker compose logs --tail=10 api
