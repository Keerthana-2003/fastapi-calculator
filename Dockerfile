# Dockerfile
FROM python:3.11-slim

# set workdir
WORKDIR /usr/src/app

# System deps for Playwright/Chromium
RUN apt-get update && apt-get install -y \
    wget \
    libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libatspi2.0-0 libxshmfence1 fonts-liberation libfontconfig1 \
    libgdk-pixbuf-2.0-0 libgtk-3-0 libx11-xcb1 libxrender1 libxtst6 \
    fonts-noto-color-emoji fonts-unifont \
 && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# copy and make startup script executable
RUN chmod +x ./wait_for_db_and_run.sh

# Install Playwright browser (chromium only to reduce size)
RUN playwright install chromium

# expose port and run (startup script waits for DB)
EXPOSE 8000
CMD ["./wait_for_db_and_run.sh"]
