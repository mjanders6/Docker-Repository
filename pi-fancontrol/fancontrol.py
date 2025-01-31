import time
import requests
from gpiozero import PWMOutputDevice

# Fan control GPIO pin
FAN_GPIO_PIN = 2  # Adjust based on your setup
fan = PWMOutputDevice(FAN_GPIO_PIN)

# Prometheus API URL
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"

# Thresholds (in Celsius)
TEMP_OFF = 25
TEMP_FULL_SPEED = 50

def get_cpu_temperature():
    """Query Prometheus for the CPU temperature."""
    query = 'node_hwmon_temp_celsius'
    try:
        response = requests.get(PROMETHEUS_URL, params={"query": query})
        data = response.json()
        if data["status"] == "success" and data["data"]["result"]:
            temp = float(data["data"]["result"][0]["value"][1])
            return temp
    except Exception as e:
        print(f"Error fetching temperature: {e}")
    return None

def set_fan_speed(temp):
    """Set fan speed based on temperature."""
    if temp < TEMP_OFF:
        fan.value = 0  # Turn fan off
    elif temp > TEMP_FULL_SPEED:
        fan.value = 1  # Full speed
    else:
        # Scale speed between TEMP_OFF and TEMP_FULL_SPEED
        fan.value = (temp - TEMP_OFF) / (TEMP_FULL_SPEED - TEMP_OFF)

if __name__ == "__main__":
    try:
        while True:
            cpu_temp = get_cpu_temperature()
            if cpu_temp is not None:
                print(f"CPU Temperature: {cpu_temp}°C")
                #set_fan_speed(cpu_temp)
            else:
                print("Failed to get temperature.")
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        fan.close()
        print("Fan control stopped.")