#!/usr/bin/env bash
set -e ITERATIONS=5 \

USERNAME="mkemalw"
PASSWORD="LM3kKb2wAoyH7enb_country-UnitedStates"
PROXY="https://${USERNAME}:${PASSWORD}@proxy.packetstream.io:31111"
VIDEO_ID="lWe_aJAYLfY"
REPLICAS=3

# Pastikan folder log ada
mkdir -p ~/yt-bot/logs

echo "🧹 Cleaning up old containers…"
docker rm -f $(docker ps -aq --filter "name=yt-bot-") > /dev/null 2>&1 || true

echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 $REPLICAS); do
  docker run -d \
    --name yt-bot-$i \
    -e PROXY_URL="$PROXY" \
    -e VIDEO_ID="$VIDEO_ID" \
    -e CONTAINER_NAME="yt-bot-$i" \
    -v ~/yt-bot/logs:/app/logs \
    yt-bot:latest
done

echo "✅ $REPLICAS bots are up!"
