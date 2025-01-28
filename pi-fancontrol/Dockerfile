# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary packages
RUN apt update && apt install -y \
    git \
    raspi-gpio \
    && rm -rf /var/lib/apt/lists/*

# Clone the pi-fancontrol repository
RUN git clone https://github.com/semu/pi-fancontrol.git /app

# Install Python dependencies
RUN pip install -r /app/requirements.txt

# Copy the fan control configuration file (if needed)
COPY pi-fancontrol.conf /app/pi-fancontrol.conf

# Run the script
CMD ["python3", "/app/pi-fancontrol.py"]
