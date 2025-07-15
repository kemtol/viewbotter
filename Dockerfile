# Dockerfile
FROM python:3.11-slim

# install Chromium & Chromedriver dari paket Debian
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/* && \
    pip install selenium

# Set env agar Selenium tahu di mana letak Chromium
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app
COPY bot.py .

ENTRYPOINT ["python", "bot.py"]
