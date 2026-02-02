# MQTT Documentation

The project integrates an MQTT client to control the clock remotely and receive status updates.

## Configuration

Configuration is done via environment variables (see [README.md](README.md)). The default base topic is `clock`.

## Subscribed Topics (Commands)

The client listens on `[MQTT_TOPIC]/#`. Here are the available sub-topics:

| Topic | Alias | Description | Payload |
|---|---|---|---|
| `time` | `clock`, `t` | Displays current time (HHMMSS) and switches to clock mode. | Ignored |
| `date` | `d` | Displays current date (DDMMYY) and switches to date mode. | Ignored |
| `show` | `display`, `set`, `s` | Displays custom text/number. | The text/number to display |
| `increment` | `i`, `inc`, `incr`, `add` | Counter mode. Initializes to 1 or increments the displayed value. | Ignored |
| `clear` | `reset`, `rst`, `clr`, `cls`, `r` | Clears display (shows 000000) and resets mode. | Ignored |
| `zero` | `zeros`, `zeroes`, `z` | Displays zeros (000000). | Ignored |
| `info` | `v`, `infos` | Requests current state publication to the `state` topic. | Ignored |

## Published Topics (State)

The client publishes information to the following topics:

### `[MQTT_TOPIC]/state`

Published on mode change or `info` request.

**Example payload:**
```json
{
  "mode": "time",
  "at": "2023-10-27 10:30:00",
  "display": "103000"
}
```

### `[MQTT_TOPIC]/start`

Published when the application starts.

**Example payload:**
```json
{
  "at": "2023-10-27 10:30:00"
}
```
