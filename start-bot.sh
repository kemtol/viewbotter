#!/usr/bin/env bash
set -e

# Sesuaikan credential & target video
USERNAME="mkemalw"
PASSWORD="LM3kKb2wAoyH7enb_country-UnitedStates"
PROXY="proxy.packetstream.io:31111"
VIDEO_ID="lWe_aJAYLfY"
REPLICAS=25

echo "🚀 Starting $REPLICAS bot containers…"
for i in $(seq 1 $REPLICAS); do
  docker run -d \
    --name yt-bot-$i \
    -e PROXY_URL="https://${USERNAME}:${PASSWORD}@${PROXY}" \
    -e VIDEO_ID="${VIDEO_ID}" \
    yt-bot:latest
done

echo "✅ $REPLICAS bots are up!"
