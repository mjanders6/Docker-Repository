FROM python:3.9-slim

WORKDIR /app

RUN apt update && apt install -y raspi-gpio && rm -rf /var/lib/apt/lists/*

COPY fancontrol.py /app/fancontrol.py

RUN pip install RPi.GPIO

CMD ["python3", "/app/fancontrol.py"]
