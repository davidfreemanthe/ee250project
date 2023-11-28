# Import necessary libraries
import paho.mqtt.client as mqtt
import time
import grovepi
from grove_rgb_lcd import *

# Sensor and Actuator Ports
LED_PORT = 5
BUZZER_PORT = 4  #  using port D4 for the Buzzer
ULTRASONIC_PORT = 7
SOUND_SENSOR_PORT = 2  #  A2 for sound sensor
LIGHT_SENSOR_PORT = 0  #  A1 for light sensor

# Thresholds for sensors
SOUND_THRESHOLD = 100  # Example threshold, adjust based on your environment
LIGHT_THRESHOLD = 300  # Example threshold, adjust based on your environment
DISTANCE_THRESHOLD = 11  # in cm, for ultrasonic sensor

# MQTT setup
USERNAME = "dthe"
MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# Initialize GPIO
grovepi.pinMode(LED_PORT, "OUTPUT")
grovepi.pinMode(BUZZER_PORT, "OUTPUT")

def trigger_alarm():
    grovepi.digitalWrite(BUZZER_PORT, 1)  # Activate buzzer
    time.sleep(1)  # Buzzer on for 1 second
    grovepi.digitalWrite(BUZZER_PORT, 0)  # Deactivate buzzer

def check_sensors_and_publish(client):
    # Read sensor values
    distance = grovepi.ultrasonicRead(ULTRASONIC_PORT)
    sound_level = grovepi.analogRead(SOUND_SENSOR_PORT)
    light_level = grovepi.analogRead(LIGHT_SENSOR_PORT)

    # Check thresholds
    if distance < DISTANCE_THRESHOLD and sound_level > SOUND_THRESHOLD and light_level > LIGHT_THRESHOLD:
        trigger_alarm()  # Trigger alarm if any condition is met

    # Publish sensor data
    client.publish(USERNAME + "/distance", str(distance))
    client.publish(USERNAME + "/sound", str(sound_level))
    client.publish(USERNAME + "/light", str(light_level))

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=60)
    client.loop_start()

    while True:
        check_sensors_and_publish(client)
        time.sleep(1)
