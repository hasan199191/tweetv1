FROM python:3.9-slim

WORKDIR /app

# Chromium ve Playwright için gerekli bağımlılıkları yükle
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    xvfb \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Pip'i güncelle
RUN pip install --upgrade pip

# Google API için ekstra paket
RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Gereksinimler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright'ı yükle
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Uygulama kodunu kopyala
COPY . .

# Çıktıların anında görünmesi için
ENV PYTHONUNBUFFERED=1

# Xvfb ile başlatmak için start.sh oluştur
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1280x720x24 &\nexport DISPLAY=:99\npython main.py' > start.sh && \
    chmod +x start.sh

# Uygulamayı çalıştır
CMD ["./start.sh"]