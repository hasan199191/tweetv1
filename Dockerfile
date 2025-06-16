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
    && rm -rf /var/lib/apt/lists/*

# Pip'i güncelle
RUN pip install --upgrade pip

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

# Uygulamayı çalıştır
CMD ["python", "main.py"]