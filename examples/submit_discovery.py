import hashlib
import os

import requests

NETWORK_URL = os.getenv("PEPTA_NETWORK_URL", "https://sandbox-api.pepta.ai/api/v1")
OPERATOR_WALLET = os.getenv("PEPTA_OPERATOR_WALLET", "0xYOUR_WALLET")
sequence = "Y-K-R-F-G-A-V-L"

payload = {
    "operator_wallet": OPERATOR_WALLET,
    "signature": "0xPLACEHOLDER",
    "agent_id": "AGENT-LOCAL-001",
    "target_id": "TGT-DEMO-001",
    "output_type": "peptide_research_output",
    "sequence_hash": "sha256:" + hashlib.sha256(sequence.encode("utf-8")).hexdigest(),
    "sequence_preview": "Y-K-*-*-G-A-*-L",
    "compute_time_ms": 14500,
    "confidence_score": 0.89,
    "local_checks": {
        "length_valid": True,
        "hydrophobicity_in_range": True,
        "synthesizability_score": 0.74,
    },
}

response = requests.post(f"{NETWORK_URL}/discoveries/submit", json=payload, timeout=30)
response.raise_for_status()
print(response.json())
