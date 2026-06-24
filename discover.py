"""
Run this once to scan the network and print Harold's device ID and local key.
Requires the Tuya IoT platform credentials (see README).

Usage:
  TUYA_API_KEY=xxx TUYA_API_SECRET=xxx TUYA_REGION=eu python3 discover.py
"""

import os
import tinytuya

api_key    = os.environ.get("TUYA_API_KEY", "")
api_secret = os.environ.get("TUYA_API_SECRET", "")
region     = os.environ.get("TUYA_REGION", "eu")  # us / eu / cn / in

if not api_key or not api_secret:
    print("Set TUYA_API_KEY, TUYA_API_SECRET, and TUYA_REGION then re-run.")
    raise SystemExit(1)

print("Scanning local network for Tuya devices...")
devices = tinytuya.deviceScan(verbose=True)
print("\nFound devices:")
for ip, info in devices.items():
    print(f"  {ip}: {info}")

print("\nAttempting cloud lookup for keys...")
c = tinytuya.Cloud(apiRegion=region, apiKey=api_key, apiSecret=api_secret)
result = c.getdevices()
for dev in result:
    print(f"\n  Name : {dev.get('name')}")
    print(f"  ID   : {dev.get('id')}")
    print(f"  Key  : {dev.get('key')}")
    print(f"  IP   : {dev.get('ip')}")
