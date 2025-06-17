# Use Ubuntu 20.04 as base image for better compatibility
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and other dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-distutils \
    python3.11-dev \
    python3-pip \
    wget \
    git \
    curl \
    unzip \
    xvfb \
    libgbm1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxrandr2 \
    libatk1.0-0 \
    libgtk-3-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libcups2 \
    libxss1 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    procps && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

# Set environment variables
ENV RENDER=true
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright
ENV DISPLAY=:99

WORKDIR /app

# Create required directories with proper permissions
RUN mkdir -p /app/browser_data /app/browser_profile /app/logs /app/ms-playwright && \
    chown -R root:root /app && \
    chmod -R 777 /app

# Install xvfb for virtual display
RUN printf '#!/bin/sh\n\
    rm -f /tmp/.X99-lock\n\
    Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp -nolisten unix &\n\
    sleep 1\n\
    exec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Install dependencies first
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Install Playwright and browsers
RUN python3 -m pip install playwright==1.40.0 && \
    playwright install chromium --with-deps && \
    playwright install-deps

# Copy source code
COPY . .

# Ensure proper permissions for runtime
RUN chmod -R 777 /app && \
    chmod +x /entrypoint.sh

# Run using entrypoint script for Xvfb
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "main.py"]
