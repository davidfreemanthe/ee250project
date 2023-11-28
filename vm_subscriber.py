import paho.mqtt.client as mqtt
import time

# MQTT setup
USERNAME = "dthe"
MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to sensor data topics
    client.subscribe(USERNAME + "/distance")
    client.subscribe(USERNAME + "/sound")
    client.subscribe(USERNAME + "/light")

# Callback for distance sensor data
def on_distance(client, userdata, message):
    distance = str(message.payload, "utf-8")
    print("Distance: " + distance + " cm")

# Callback for sound sensor data
def on_sound(client, userdata, message):
    sound_level = str(message.payload, "utf-8")
    print("Sound Level: " + sound_level)

# Callback for light sensor data
def on_light(client, userdata, message):
    light_level = str(message.payload, "utf-8")
    print("Light Level: " + light_level)

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Assign individual callbacks for each sensor
    client.message_callback_add(USERNAME + "/distance", on_distance)
    client.message_callback_add(USERNAME + "/sound", on_sound)
    client.message_callback_add(USERNAME + "/light", on_light)

    client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=60)
    client.loop_start()

    while True:
        time.sleep(1)
