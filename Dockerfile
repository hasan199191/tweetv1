FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Update Python to 3.9+
RUN apt-get update && apt-get install -y python3.9
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

WORKDIR /app

# Install pip for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py

# Install dependencies
COPY requirements.txt .
RUN python3.9 -m pip install -r requirements.txt

# Copy source code
COPY . .

# Create browser_data directory for persistent session
RUN mkdir -p browser_data

# Install Playwright browsers
RUN playwright install chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python3.9", "main.py"]
