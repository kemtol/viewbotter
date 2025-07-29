#!/usr/bin/env bash
set -euo pipefail

# 1. Muat variabel dari .env
if [ -f .env ]; then
  export $(grep -v '^\s*#' .env | xargs)
fi

# 2. Validasi mandatory env vars
: "${PS_HOST:?PS_HOST not set in .env}"
: "${PS_PORT:?PS_PORT not set in .env}"
: "${PS_USER:?PS_USER not set in .env}"
: "${PS_PASS:?PS_PASS not set in .env}"
: "${VIDEO_ID:?VIDEO_ID not set in .env}"
: "${REPLICAS:?REPLICAS not set in .env}"

# 3. Bentuk PROXY_URL
PROXY_URL="http://${PS_USER}:${PS_PASS}@${PS_HOST}:${PS_PORT}"

# 4. Siapkan folder log
mkdir -p logs

# 5. Bersihkan container lama
echo "🧹 Cleaning up old yt-bot containers…"
docker rm -f $(docker ps -aq --filter "name=yt-bot-") > /dev/null 2>&1 || true

# 6. Spin up container baru
echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 "$REPLICAS"); do
  docker run -d \
    --name yt-bot-$i \
    -e PROXY_URL="$PROXY_URL" \
    -e VIDEO_ID="$VIDEO_ID" \
    -v "$(pwd)/logs":/app/logs \
    yt-bot:latest
  sleep 0.5
done

echo "✅ $REPLICAS bots are up!"
