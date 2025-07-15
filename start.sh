#!/usr/bin/env bash
set -e

echo "🔨 Building Docker image yt-bot:latest…"
docker build -t yt-bot:latest .
echo "✅ Image built."
