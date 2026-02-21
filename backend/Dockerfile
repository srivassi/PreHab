# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8080

# Run uvicorn on port 8080 (Cloud Run requirement)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
