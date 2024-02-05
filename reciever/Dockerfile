# Use an official Python runtime as a base image
FROM python:3

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY src/ src/
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    libusb-1.0-0 \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

# Add Poppler to the PATH
ENV PATH="${PATH}:/usr/bin"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


ENV SECRET_KEY=secret_key

# Set the entry point
CMD ["python", "src/main.py"]