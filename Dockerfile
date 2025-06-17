FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set environment variable to indicate we're running on Render
ENV RENDER=true

# Install Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils python3.11-dev

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

WORKDIR /app

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Upgrade pip
RUN python3.11 -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p browser_data
RUN mkdir -p /app/logs

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/browser_data

# Run the bot with Python 3.11
CMD ["python3.11", "main.py"]
