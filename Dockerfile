FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SELENIUM_REMOTE_URL="http://chrome:4444"

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Run the scraper
CMD ["python", "scraper.py"]
