import hashlib
import os
import time
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

NETWORK_URL = os.getenv("PEPTA_NETWORK_URL", "https://sandbox-api.pepta.ai/api/v1")
OPERATOR_WALLET = os.getenv("PEPTA_OPERATOR_WALLET")
OPERATOR_KEY = os.getenv("PEPTA_OPERATOR_KEY")
AGENT_ID = os.getenv("PEPTA_AGENT_ID", "AGENT-LOCAL-001")

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
HYDROPHOBIC = set("AILMFWYV")


def require_env() -> None:
    if not OPERATOR_WALLET:
        raise RuntimeError("Missing PEPTA_OPERATOR_WALLET.")
    if not OPERATOR_KEY:
        raise RuntimeError("Missing PEPTA_OPERATOR_KEY.")


def fetch_targets(limit: int = 5) -> Dict[str, Any]:
    response = requests.get(
        f"{NETWORK_URL}/targets",
        params={"limit": limit, "status": "open"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_target(target_id: str) -> Dict[str, Any]:
    response = requests.get(f"{NETWORK_URL}/targets/{target_id}", timeout=30)
    response.raise_for_status()
    return response.json()


def placeholder_generate_sequence(constraints: Dict[str, Any]) -> str:
    min_len = int(constraints.get("min_length", 8))
    max_len = int(constraints.get("max_length", 25))
    required_motifs = constraints.get("required_motifs", [])
    length = max(min_len, min(max_len, 10))

    residues = [motif for motif in required_motifs if motif in AMINO_ACIDS]
    base = list(AMINO_ACIDS)
    while len(residues) < length:
        residues.append(base[(len(residues) * 7) % len(base)])
    return "-".join(residues[:length])


def sequence_hash(sequence: str) -> str:
    return "sha256:" + hashlib.sha256(sequence.encode("utf-8")).hexdigest()


def sequence_preview(sequence: str) -> str:
    residues = sequence.split("-")
    if len(residues) <= 4:
        return "-".join(residues)
    masked = []
    for index, residue in enumerate(residues):
        if index < 2 or index >= len(residues) - 2:
            masked.append(residue)
        else:
            masked.append("*")
    return "-".join(masked)


def hydrophobicity_index(sequence: str) -> float:
    residues = sequence.replace("-", "")
    if not residues:
        return 0.0
    hydrophobic_count = sum(1 for aa in residues if aa in HYDROPHOBIC)
    return round((hydrophobic_count / len(residues)) * 2 - 1, 3)


def run_local_checks(sequence: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
    residues = sequence.replace("-", "")
    min_len = int(constraints.get("min_length", 0))
    max_len = int(constraints.get("max_length", 999))
    allowed = set(constraints.get("allowed_residues", AMINO_ACIDS))
    hydrophobicity_range = constraints.get("hydrophobicity_range", [-1.0, 1.0])
    hydro = hydrophobicity_index(sequence)

    return {
        "length_valid": min_len <= len(residues) <= max_len,
        "alphabet_valid": all(aa in allowed for aa in residues),
        "hydrophobicity_index": hydro,
        "hydrophobicity_in_range": hydrophobicity_range[0] <= hydro <= hydrophobicity_range[1],
        "synthesizability_score": 0.74,
        "toxicity_flag": residues.count("C") >= 3 or "WWW" in residues,
    }


def sign_payload_placeholder(payload: Dict[str, Any]) -> str:
    signing_material = str(sorted(payload.items())) + str(OPERATOR_KEY)
    return "0x" + hashlib.sha256(signing_material.encode("utf-8")).hexdigest()


def submit_discovery(target_id: str, sequence: str, checks: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "operator_wallet": OPERATOR_WALLET,
        "agent_id": AGENT_ID,
        "target_id": target_id,
        "output_type": "peptide_research_output",
        "sequence_hash": sequence_hash(sequence),
        "sequence_preview": sequence_preview(sequence),
        "compute_time_ms": 14500,
        "confidence_score": 0.89,
        "local_checks": checks,
        "metadata": {
            "model_family": "placeholder",
            "notes": "Sandbox research output. Not intended for medical or clinical use.",
        },
    }
    payload["signature"] = sign_payload_placeholder(payload)

    response = requests.post(
        f"{NETWORK_URL}/discoveries/submit",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def run_node_once(target_id: str) -> None:
    require_env()
    print("[*] PEPTA node initialized.")
    target = fetch_target(target_id)
    print(f"[*] Loaded target: {target.get('name', target_id)}")
    constraints = target.get("constraints", {})
    print("[*] Generating sandbox research output...")
    sequence = placeholder_generate_sequence(constraints)
    print("[*] Running local checks...")
    checks = run_local_checks(sequence, constraints)

    if not checks["length_valid"] or not checks["alphabet_valid"]:
        print("[!] Local checks failed. Output not submitted.")
        print(checks)
        return

    print("[*] Submitting hashed research output...")
    result = submit_discovery(target_id, sequence, checks)
    print("[*] Submission response:")
    print(result)


def run_node_loop(poll_seconds: int = 120) -> None:
    require_env()
    while True:
        try:
            targets_response = fetch_targets(limit=1)
            targets = targets_response.get("targets", [])
            if not targets:
                print("[*] No open targets found.")
            else:
                run_node_once(targets[0]["target_id"])
        except Exception as exc:
            print(f"[!] Node cycle failed: {exc}")

        print(f"[*] Sleeping for {poll_seconds} seconds...")
        time.sleep(poll_seconds)


if __name__ == "__main__":
    run_node_once("TGT-DEMO-001")
