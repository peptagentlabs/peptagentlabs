import os

import requests

NETWORK_URL = os.getenv("PEPTA_NETWORK_URL", "https://sandbox-api.pepta.ai/api/v1")

response = requests.get(f"{NETWORK_URL}/targets", params={"status": "open", "limit": 10}, timeout=30)
response.raise_for_status()
print(response.json())
