#!/usr/bin/env bash
set -euo pipefail

# 1) Load .env (jika ada)
if [ -f .env ]; then
  export $(grep -v '^\s*#' .env | xargs)
fi

# 2) Cek mandatory vars
: "${PS_HOST:?PS_HOST not set in .env}"
: "${PS_PORT:?PS_PORT not set in .env}"
: "${PS_USER:?PS_USER not set in .env}"
: "${PS_PASS:?PS_PASS not set in .env}"
: "${VIDEO_ID:?VIDEO_ID not set in .env}"
: "${REPLICAS:?REPLICAS not set in .env}"

# 3) Bersihkan semua container yt-bot-* yang masih ada
echo "🧹 Cleaning up old yt-bot containers…"
OLD_CONTAINERS=$(docker ps -a -q --filter "name=^/yt-bot-[0-9]+$")
if [ -n "$OLD_CONTAINERS" ]; then
  docker rm -f $OLD_CONTAINERS
fi

# 4) Spin up baru
echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 "$REPLICAS"); do
  # Pastikan kalau-kalau ada sisa dengan nama yang sama
  docker rm -f yt-bot-"$i" 2>/dev/null || true

  docker run --rm -d \
    --name yt-bot-"$i" \
    -e PROXY_URL="http://${PS_USER}:${PS_PASS}@${PS_HOST}:${PS_PORT}" \
    -e VIDEO_ID="${VIDEO_ID}" \
    yt-bot:latest
done

echo "✅ $REPLICAS bots are up (auto‑removed after exit)!"
