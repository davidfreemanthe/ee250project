# Import necessary libraries
import paho.mqtt.client as mqtt
import time
import grovepi
from grove_rgb_lcd import *
import datetime
from flask import Flask, render_template
import threading

# Sensor and Actuator Ports
LED_PORT = 5
BUZZER_PORT = 4  # Using port D4 for the Buzzer
ULTRASONIC_PORT = 7
SOUND_SENSOR_PORT = 2  # A2 for sound sensor
LIGHT_SENSOR_PORT = 0  # A1 for light sensor

# Thresholds for sensors
SOUND_THRESHOLD = 100  # Example threshold, adjust based on your environment
LIGHT_THRESHOLD = 300  # Example threshold, adjust based on your environment
DISTANCE_THRESHOLD = 11  # in cm, for ultrasonic sensor

# MQTT setup
USERNAME = "dthe"
MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883

# Flask app
app = Flask(__name__)

# Initialize GPIO
grovepi.pinMode(LED_PORT, "OUTPUT")
grovepi.pinMode(BUZZER_PORT, "OUTPUT")

# MQTT Connection Callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def trigger_alarm():
    grovepi.digitalWrite(BUZZER_PORT, 1)  # Activate buzzer
    time.sleep(1)  # Buzzer on for 1 second
    grovepi.digitalWrite(BUZZER_PORT, 0)  # Deactivate buzzer

def log_security_breach(distance, sound_level, light_level):
    with open("security_breaches.log", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}: Breach detected. Distance: {distance} cm, Sound: {sound_level}, Light: {light_level}\n")

def check_sensors_and_publish(client):
    # Read sensor values
    distance = grovepi.ultrasonicRead(ULTRASONIC_PORT)
    sound_level = grovepi.analogRead(SOUND_SENSOR_PORT)
    light_level = grovepi.analogRead(LIGHT_SENSOR_PORT)

    # Check thresholds
    if distance < DISTANCE_THRESHOLD and sound_level > SOUND_THRESHOLD and light_level > LIGHT_THRESHOLD:
        trigger_alarm()  # Trigger alarm if all conditions are met
        log_security_breach(distance, sound_level, light_level)  # Log the security breach

    # Publish sensor data
    client.publish(USERNAME + "/distance", str(distance))
    client.publish(USERNAME + "/sound", str(sound_level))
    client.publish(USERNAME + "/light", str(light_level))

@app.route('/')
def index():
    try:
        with open("security_breaches.log", "r") as file:
            breaches = file.readlines()
    except FileNotFoundError:
        breaches = ["No breaches recorded."]
    return render_template('index.html', breaches=breaches)

def start_flask_app():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()

    # MQTT client setup
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=60)
    client.loop_start()

    while True:
        check_sensors_and_publish(client)
        time.sleep(1)


