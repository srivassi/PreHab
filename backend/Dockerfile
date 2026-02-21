# Use Python 3.11 slim image — required for scikit-learn==1.5.2 compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install system build deps required for packages like numpy
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   gfortran \
	   python3-dev \
	   libopenblas-dev \
	   liblapack-dev \
	   pkg-config \
	&& rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python deps
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8080

# Run uvicorn on port 8080 (Cloud Run requirement)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]