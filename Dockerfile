FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

WORKDIR /app

# Gereksinimler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Browser'ı yükle
RUN playwright install chromium
RUN playwright install-deps chromium

# Uygulama kodunu kopyala
COPY . .

# Çıktıların anında görünmesi için
ENV PYTHONUNBUFFERED=1

# Uygulamayı çalıştır
CMD ["python", "main.py"]