"""
How hot is Harold?
Flask web server that polls Harold (Tuya heater @ 192.168.1.237:6668)
and exposes his current state via a simple dashboard.
"""

import os
import time
import threading
import tinytuya
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()

HAROLD_IP = "192.168.1.237"
HAROLD_PORT = 6668
HAROLD_ID = os.environ.get("HAROLD_ID", "")
HAROLD_KEY = os.environ.get("HAROLD_KEY", "")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "5"))
TUYA_API_KEY = os.environ.get("TUYA_API_KEY", "")
TUYA_API_SECRET = os.environ.get("TUYA_API_SECRET", "")
TUYA_REGION = os.environ.get("TUYA_REGION", "eu")
SHADOW_INTERVAL = int(os.environ.get("SHADOW_INTERVAL", "60"))

app = Flask(__name__)

_state: dict = {"Error": "No data yet", "ts": 0}
_lock = threading.Lock()


def make_cloud():
    return tinytuya.Cloud(
        apiRegion=TUYA_REGION,
        apiKey=TUYA_API_KEY,
        apiSecret=TUYA_API_SECRET,
        apiDeviceID=HAROLD_ID,
    )


def poll_shadow():
    while True:
        try:
            c = make_cloud()
            r = c.cloudrequest(f"/v2.0/cloud/thing/{HAROLD_ID}/shadow/properties")
            if r.get("success"):
                shadow = {p["code"]: p["time"] for p in r["result"]["properties"]}
                with _lock:
                    _state["shadow"] = shadow
        except Exception:
            pass
        time.sleep(SHADOW_INTERVAL)


def make_device():
    d = tinytuya.OutletDevice(
        dev_id=HAROLD_ID,
        address=HAROLD_IP,
        local_key=HAROLD_KEY,
        version=3.3,
    )
    d.set_socketPersistent(False)
    return d


def poll_harold():
    while True:
        try:
            d = make_device()
            raw = d.status()
            with _lock:
                shadow = _state.get("shadow")
                _state.clear()
                _state.update(raw)
                _state["ts"] = time.time()
                if shadow:
                    _state["shadow"] = shadow
        except Exception as exc:
            with _lock:
                shadow = _state.get("shadow")
                _state.clear()
                _state["Error"] = str(exc)
                _state["ts"] = time.time()
                if shadow:
                    _state["shadow"] = shadow
        time.sleep(POLL_INTERVAL)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    with _lock:
        state = dict(_state)
    return jsonify(state)


if __name__ == "__main__":
    if not HAROLD_ID or not HAROLD_KEY:
        print(
            "\n*** ERROR: Set HAROLD_ID and HAROLD_KEY environment variables. ***\n"
            "See README.md for how to get them from the Tuya IoT platform.\n"
        )
        raise SystemExit(1)

    t = threading.Thread(target=poll_harold, daemon=True)
    t.start()
    if TUYA_API_KEY and TUYA_API_SECRET:
        threading.Thread(target=poll_shadow, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
