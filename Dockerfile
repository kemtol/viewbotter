FROM python:3.11-slim

# Install Chromium, Chromedriver & Selenium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      chromium chromium-driver && \
    pip install selenium && \
    rm -rf /var/lib/apt/lists/*

# Biar Selenium tahu lokasi browser & driver
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Salin script bot
COPY bot.py /app/bot.py

ENTRYPOINT ["python3", "bot.py"]
