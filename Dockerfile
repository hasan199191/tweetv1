FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Create browser_data directory for persistent session
RUN mkdir -p browser_data

# Install Playwright browsers
RUN playwright install chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
