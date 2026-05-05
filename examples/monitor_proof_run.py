import os
import time

import requests

NETWORK_URL = os.getenv("PEPTA_NETWORK_URL", "https://sandbox-api.pepta.ai/api/v1")
PROOF_RUN_ID = os.getenv("PEPTA_PROOF_RUN_ID", "PR-8821")

while True:
    response = requests.get(f"{NETWORK_URL}/proof-runs", timeout=30)
    response.raise_for_status()
    proof_runs = response.json().get("proof_runs", [])
    match = next((item for item in proof_runs if item["proof_run_id"] == PROOF_RUN_ID), None)
    if match:
        print(match)
    else:
        print(f"Proof Run {PROOF_RUN_ID} not found.")
    time.sleep(60)
