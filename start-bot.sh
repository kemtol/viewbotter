#!/usr/bin/env bash
set -euo pipefail

# Muat variabel dari .env (jika ada)
if [ -f .env ]; then
  export $(grep -v '^\s*#' .env | xargs)
fi

# Pastikan semua variabel wajib sudah di‑set
: "${PS_HOST:?PS_HOST tidak ditemukan di .env}"
: "${PS_PORT:?PS_PORT tidak ditemukan di .env}"
: "${PS_USER:?PS_USER tidak ditemukan di .env}"
: "${PS_PASS:?PS_PASS tidak ditemukan di .env}"
: "${VIDEO_ID:?VIDEO_ID tidak ditemukan di .env}"
: "${REPLICAS:?REPLICAS tidak ditemukan di .env}"

echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 "$REPLICAS"); do
  docker run --rm -d \
    --name yt-bot-"$i" \
    -e PROXY_URL="http://${PS_USER}:${PS_PASS}@${PS_HOST}:${PS_PORT}" \
    -e VIDEO_ID="${VIDEO_ID}" \
    yt-bot:latest
done

echo "✅ $REPLICAS bots are up (auto‑removed after exit)!"
