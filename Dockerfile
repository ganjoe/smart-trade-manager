FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV STM_CONFIG_FILE config.json

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
# Copy the actual config into the image
COPY config.json ./config.json

# Entry point
CMD ["python", "-m", "src.main"]
