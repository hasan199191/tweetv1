# Use Ubuntu 20.04 as base image
FROM mcr.microsoft.com/playwright/python:v1.41.0-focal

# Install Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-distutils \
    python3.11-dev \
    python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV DISPLAY=:99
ENV RENDER=true

# Ensure Xvfb is installed
RUN apt-get install -y xvfb

# Create required directories
RUN mkdir -p /app /browsers /app/browser_data /app/browser_profile /app/logs && \
    chmod -R 777 /app /browsers

WORKDIR /app

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

# Install Playwright properly
RUN DEBIAN_FRONTEND=noninteractive python3 -m pip install --upgrade pip && \
    python3 -m pip install playwright==1.40.0 && \
    python3 -m playwright install --with-deps chromium && \
    python3 -m playwright install-deps chromium

# Copy source code
COPY . .

# Set up for Playwright
ENV PYTHONPATH=/app
ENV NODE_PATH=/usr/lib/node_modules
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Create Playwright directory
RUN mkdir -p /ms-playwright && chmod 777 /ms-playwright

# Install additional dependencies for Playwright
RUN apt-get update && apt-get install -y \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    lsb-release \
    xdg-utils \
    wget \
    xvfb && \
    rm -rf /var/lib/apt/lists/*

# Ensure proper permissions
RUN mkdir -p /app/browser_data /app/browser_profile /app/logs && \
    chmod -R 777 /app && \
    chmod +x /entrypoint.sh

# Update entrypoint to include debug info
RUN printf '#!/bin/sh\n\
    echo "Starting Xvfb..."\n\
    rm -f /tmp/.X99-lock\n\
    Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp -nolisten unix &\n\
    echo "Waiting for Xvfb..."\n\
    sleep 2\n\
    echo "DISPLAY=$DISPLAY"\n\
    echo "Checking Playwright installation..."\n\
    python3 -m playwright install chromium\n\
    echo "Starting application..."\n\
    exec "$@"\n' > /entrypoint.sh

# Run using entrypoint script for Xvfb
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "-u", "main.py"]
