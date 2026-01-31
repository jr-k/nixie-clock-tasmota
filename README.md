# Nixie Clock Tasmota

A Python script to control a Nixie Clock via Tasmota and MQTT.

## Features

- Syncs time and date to the clock.
- Supports MQTT for remote control and status updates.
- Configurable via Environment Variables.
- Docker support.

## Configuration

The application is configured using environment variables.

| Variable | Default | Description |
|---|---|---|
| `TASMOTA_HOST` | `192.168.1.103` | IP address or hostname of the Tasmota device. |
| `MQTT_TOPIC` | `clock` | Base MQTT topic. |
| `ENABLE_MQTT` | `true` | Set to `false` to disable MQTT functionality. |
| `MQTT_HOST` | `localhost` | MQTT Broker hostname. |
| `MQTT_PORT` | `1883` | MQTT Broker port. |
| `MQTT_USERNAME` | *(empty)* | MQTT Username (optional). |
| `MQTT_PASSWORD` | *(empty)* | MQTT Password (optional). |

## Installation & Running

### Using Docker Compose (Recommended for Dev)

1. **Build and Run:**
   ```bash
   docker-compose up --build
   ```

2. **Configure:**
   You can set environment variables in a `.env` file or inline:
   ```bash
   TASMOTA_HOST=192.168.1.50 docker-compose up
   ```

### Using Docker

1. **Build the image:**
   ```bash
   docker build -t nixie-clock .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -e TASMOTA_HOST=192.168.1.50 \
     -e ENABLE_MQTT=false \
     --name my-nixie-clock \
     nixie-clock
   ```

### Running Locally (Python)

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the script:**
   ```bash
   export TASMOTA_HOST=192.168.1.50
   python3 clock.py
   ```
