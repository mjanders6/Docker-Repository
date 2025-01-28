# Use a full Debian-based Python image instead of slim
FROM python:3.9-bullseye

WORKDIR /app

# Update package lists and install necessary tools
RUN apt update && apt install -y \
    #raspberrypi-kernel \
    #raspberrypi-bootloader \
    raspi-gpio \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the fan control script
COPY fancontrol.py /app/fancontrol.py

# Install Python dependencies
RUN pip install RPi.GPIO

# Run the script
CMD ["python3", "/app/fancontrol.py"]
