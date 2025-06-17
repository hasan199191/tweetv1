# Use Python 3.11 based Playwright image
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Install Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

# Set environment variable to indicate we're running on Render
ENV RENDER=true
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Playwright and browsers BEFORE copying the app
RUN python3 -m pip install playwright==1.40.0 && \
    playwright install chromium && \
    playwright install-deps chromium

# Install dependencies
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy source code
COPY . .

# Create log directory
RUN mkdir -p /app/logs

# Run the bot
CMD ["python3", "main.py"]
