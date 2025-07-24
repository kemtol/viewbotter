#!/usr/bin/env bash
set -euo pipefail

# Load env
if [ -f .env ]; then
  export $(grep -v '^\s*#' .env | xargs)
fi

# Sanity check
: "${PS_HOST:?PS_HOST not set}"
: "${PS_PORT:?PS_PORT not set}"
: "${PS_USER:?PS_USER not set}"
: "${PS_PASS:?PS_PASS not set}"
: "${VIDEO_ID:?VIDEO_ID not set}"
: "${REPLICAS:?REPLICAS not set}"

# Clean up any leftover bots from prior runs
echo "🧹 Cleaning up old yt-bot containers…"
docker rm -f yt-bot-* 2> /dev/null || true

# Launch new bots
echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 "$REPLICAS"); do
  docker run --rm -d \
    --name yt-bot-"$i" \
    -e PROXY_URL="http://${PS_USER}:${PS_PASS}@${PS_HOST}:${PS_PORT}" \
    -e VIDEO_ID="${VIDEO_ID}" \
    yt-bot:latest
done

echo "✅ $REPLICAS bots are up (auto‑removed after exit)!"
