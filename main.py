import json
import time
import seeed_dht
import paho.mqtt.publish as publish
from grove.grove_4_digit_display import Grove4DigitDisplay

# sleep for system to correctly boot and connect to wifi
time.sleep(20)

# configure sensors
display = Grove4DigitDisplay(16, 17)  # Using 4 digit display
temphum = seeed_dht.DHT("11", 5)  # Using DHT11 sensor

# read from settings file using json
with open("/home/pi/settings.json", "r") as f:
    settings = json.load(f)

# configure mqtt settings in settings.json file !!!
mqtt_host = settings["mqtt_host"]
mqtt_port = settings["mqtt_port"]
mqtt_client_id = settings["mqtt_client_id"]
mqtt_user = settings["mqtt_user"]
mqtt_password = settings["mqtt_password"]
mqtt_topic = settings["mqtt_topic"]

# configure debug mode in settings.json file !!!
debug = settings["debug"]

# initialize variables
mqtt_payload = None
humi, temp, old_humi, old_temp = None, None, None, None

# initialize display
display.show("----")

while True:
    # read from sensors
    humi, temp = temphum.read()

    # if humidity or temperature changed, create mqtt payload and publish
    if (humi != old_humi or temp != old_temp) and humi and temp:

        # payload creation
        mqtt_payload = ""

        ## if temperature changed, add to mqtt payload
        if temp != old_temp:
            mqtt_payload += f"&field1={temp}"

        ## if humidity changed, add to mqtt payload
        if humi != old_humi:
            mqtt_payload += f"&field2={humi}"

        ## add status to mqtt payload
        mqtt_payload += "&status=MQTTPUBLISH"

        ## publish mqtt payload
        publish.single(
            hostname=mqtt_host,
            port=mqtt_port,
            client_id=mqtt_client_id,
            auth={"username": mqtt_user, "password": mqtt_password},
            topic=mqtt_topic,
            payload=mqtt_payload,
        )

        ## if debug is enabled, print values
        if debug:
            print("---")
            print(f"Temp: {temp} C")
            print(f"Humi: {humi} %")
            print()

    # if humi and temp have value, display on 4 digit display
    if humi and temp:
        display.show(f"{int(temp):>2} C")
        time.sleep(5)
        display.show(f"{int(humi):>2} H")
        time.sleep(1)

    # save old values
    old_temp = temp
    old_humi = humi
