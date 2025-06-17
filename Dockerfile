FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set environment variable to indicate we're running on Render
ENV RENDER=true

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

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

# Run the bot
CMD ["python", "main.py"]
