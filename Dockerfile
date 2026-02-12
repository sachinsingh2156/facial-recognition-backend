# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install system dependencies for face_recognition and dlib
# Using --no-install-recommends to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential cmake \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    libboost-python-dev libboost-thread-dev \
    libssl-dev libffi-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy requirements first for better Docker layer caching
COPY facial_recognition_system/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make port 8053 available to the world outside this container
EXPOSE 8053

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run migrations and start the Django server (cross-platform)
CMD ["sh", "-c", "python facial_recognition_system/manage.py migrate && python facial_recognition_system/manage.py runserver 0.0.0.0:8053"]
