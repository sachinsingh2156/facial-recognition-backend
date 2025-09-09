# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install system dependencies for face_recognition and dlib
RUN apt-get update && \
    apt-get install -y build-essential cmake \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    libboost-python-dev libboost-thread-dev \
    libssl-dev libffi-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r facial_recognition_system/requirements.txt

# Make port 8053 available to the world outside this container
EXPOSE 8053

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the command to start the Django server
CMD ["python", "facial_recognition_system/manage.py", "runserver", "0.0.0.0:8053"] 