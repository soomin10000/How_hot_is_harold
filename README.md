# How Hot is Harold?

Web dashboard for Harold, a Tuya smart heater at `192.168.1.237:6668`.

## Protocol

Harold speaks **Tuya local protocol v3.3** (AES-128-ECB encrypted).
You need two device-specific values to talk to him:

| Value | Where to get it |
|-------|----------------|
| **Device ID** | Tuya IoT Platform → Cloud → My Project → Devices tab |
| **Local Key** (16 chars) | Same page, or extracted via `discover.py` |

## Getting the credentials

1. Create a free account at [iot.tuya.com](https://iot.tuya.com)
2. Create a Cloud project (any type), add your device
3. Under **Devices → Device Management**, find Harold and copy the **Device ID**
4. The **Local Key** appears next to the device (may need "Debug Device" enabled)

Or run `discover.py` with your API credentials to fetch both automatically.

## Running

```bash
cp .env.example .env
# edit .env with your HAROLD_ID and HAROLD_KEY
source .env
.venv/bin/python3 harold.py
```

Open http://localhost:5000

## API

- `GET /` — dashboard (auto-refreshes every 5s)
- `GET /api/status` — raw JSON from Harold

## Files

```
harold.py       main Flask app + polling thread
discover.py     one-time tool to find device ID and local key
templates/      Jinja2 HTML templates
.env.example    environment variable template
```
