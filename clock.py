#!/bin/python3
import paho.mqtt.client as mqtt
import requests
import time
import threading
import json
import os
from datetime import datetime

# Configuration via Environment Variables
TASMOTA_HOST = os.getenv('TASMOTA_HOST', '192.168.1.103')
ENABLE_MQTT = os.getenv('ENABLE_MQTT', 'true').lower() == 'true'
TZ = os.getenv('TZ', 'Europe/Paris')

if TZ:
    os.environ['TZ'] = TZ
    time.tzset()

# MQTT Configuration
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'clock')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')

TASMOTA_URL = "http://{}/cm".format(TASMOTA_HOST)

client = None

# Util functions
def pad_with_zeros(s):
    s = ''.join(filter(str.isdigit, s))
    return s.zfill(6)[:6]

# All clock modes and display state
MODE_TIME = 'time'
MODE_RESET = 'reset'
MODE_DATE = 'date'
MODE_INCR = 'increment'
MODE_CUST = 'custom'

MODE = MODE_TIME
DISPLAY = "000000"

def notify_state():
    global MODE, DISPLAY, client
    if not ENABLE_MQTT or client is None:
        return
    try:
        client.publish(MQTT_TOPIC + "/state", json.dumps({
            "mode": MODE,
            "at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "display": DISPLAY
        }))
    except Exception as e:
        print(f"MQTT Publish Error: {e}")

def s_display(msg):
    global DISPLAY
    DISPLAY = pad_with_zeros(str(msg))
    #print(f'Display: {DISPLAY}')

def s_mode(smode):
    global MODE, DISPLAY
    #print(f'Mode: {smode}')
    MODE = smode
    notify_state()

def s_mode_reset():
    s_mode(MODE_RESET)

def s_mode_date():
    s_mode(MODE_DATE)

def s_mode_time():
    s_mode(MODE_TIME)

def s_mode_incr():
    s_mode(MODE_INCR)

def s_mode_cust():
    s_mode(MODE_CUST)

# Mqtt callbacks
def on_message(client, userdata, message):
    global MODE, DISPLAY
    fulltopic = message.topic
    topic = '/'.join(fulltopic.split('/')[1:])
    payload = str(message.payload.decode("utf-8"))

    if topic == 'zero' or topic == 'zeros' or topic == 'zeroes' or topic == 'z':
        s_display('000000')
        s_mode_reset()
        requests.get(TASMOTA_URL, params={'cmnd': 'SerialSend2 r'})
    elif topic == 'clear' or topic == 'reset' or topic == 'rst' or topic == 'clr' or topic == 'cls' or topic == 'r':
        s_display('000000')
        s_mode_reset()
        requests.get(TASMOTA_URL, params={'cmnd': 'SerialSend2 b'})
    elif topic == 'increment' or topic == 'i' or topic == 'inc' or topic == 'incr' or topic == 'add':
        if MODE != MODE_INCR:
            s_display('000001')
            requests.get(TASMOTA_URL, params={'cmnd': 'SerialSend2 b'})
        else:
            s_display(int(DISPLAY) + 1)

        s_mode_incr()
        requests.get(TASMOTA_URL, params={'cmnd': 'SerialSend2 i'})
    elif topic == 'time' or topic == 'clock' or topic == 't':
        s_display(time.strftime('%H%M%S'))
        s_mode_time()
    elif topic == 'date' or topic == 'd':
        s_display(time.strftime('%d%m%y'))
        s_mode_date()
    elif topic == 'info' or topic == 'v' or topic == 'infos':
        notify_state()
    elif topic == 'show' or topic == 'display' or topic == 'set' or topic == 's':
        requests.get(TASMOTA_URL, params={'cmnd': 'SerialSend2 b'})
        s_display(payload)
        s_mode_cust()
        payload = {'cmnd': f'SerialSend2 {DISPLAY}'}
        try:
            requests.get(TASMOTA_URL, params=payload)
        except requests.RequestException as e:
            print(f"Tasmota request error : {e}")

def on_log(client, userdata, level, buf):
    if level == mqtt.MQTT_LOG_ERR:
        print("Error:", buf)

# Initialize MQTT if enabled
if ENABLE_MQTT:
    print(f"Initializing MQTT connection to {MQTT_HOST}:{MQTT_PORT}...")
    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    try:
        client.connect(MQTT_HOST, MQTT_PORT)
        
        # Mqtt subscribe
        client.subscribe(MQTT_TOPIC + "/#")
        client.on_message = on_message
        client.on_log = on_log

        # Mqtt thread start
        mqtt_thread = threading.Thread(target=client.loop_start)
        mqtt_thread.start()

        # Startup configuration
        start_payload = json.dumps({"at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        client.publish(MQTT_TOPIC + "/start", start_payload)
        client.publish(MQTT_TOPIC + "/clear", start_payload)
        client.publish(MQTT_TOPIC + "/time", start_payload)
        print("MQTT initialized and started.")
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")
        print("Continuing without MQTT.")
        client = None
else:
    print("MQTT is disabled via configuration.")

# Initial display set
s_display(0)

# Main loop for timed events
print("Starting main loop...")
while True:
    if MODE == MODE_TIME:
        current_time = time.strftime('%H%M%S')
        s_display(current_time)
        payload = {'cmnd': f'SerialSend2 {current_time}'}
        try:
            requests.get(TASMOTA_URL, params=payload)
        except requests.RequestException as e:
            print(f"Tasmota request error : {e}")
    elif MODE == MODE_DATE:
        current_date = time.strftime('%d%m%y')
        s_display(current_date)
        payload = {'cmnd': f'SerialSend2 {current_date}'}
        try:
            requests.get(TASMOTA_URL, params=payload)
        except requests.RequestException as e:
            print(f"Tasmota request error : {e}")
    time.sleep(1)
