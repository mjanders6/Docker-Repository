FROM balenalib/raspberrypi3-debian:latest

WORKDIR /app

# Update package lists and install GPIO tools
RUN apt update && apt install -y \
    raspberrypi-kernel \
    raspberrypi-bootloader \
    raspi-gpio \
    && rm -rf /var/lib/apt/lists/*

# Copy the fan control script
COPY fancontrol.py /app/fancontrol.py

# Install Python dependencies
RUN pip install RPi.GPIO

# Run the script
CMD ["python3", "/app/fancontrol.py"]
