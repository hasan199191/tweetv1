FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set environment variable to indicate we're running on Render
ENV RENDER=true

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright and browsers BEFORE copying the app
RUN playwright install chromium
RUN playwright install-deps chromium

# Set the browser path environment variable
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
