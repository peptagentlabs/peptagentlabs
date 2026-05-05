import csv
import hashlib
import random
from pathlib import Path

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
TARGET_FAMILIES = [
    "benchmark_kinase",
    "benchmark_gpcr",
    "benchmark_enzyme",
    "benchmark_receptor",
]
HYDROPHOBIC = set("AILMFWYV")
CHARGED = set("DEKRH")
MOTIFS = {
    "benchmark_kinase": ["Y", "K"],
    "benchmark_gpcr": ["R", "F"],
    "benchmark_enzyme": ["H", "D"],
    "benchmark_receptor": ["Q", "L"],
}


def sequence_hash(sequence: str) -> str:
    return "sha256:" + hashlib.sha256(sequence.encode("utf-8")).hexdigest()


def generate_sequence(min_len: int = 8, max_len: int = 25) -> str:
    length = random.randint(min_len, max_len)
    residues = [random.choice(AMINO_ACIDS) for _ in range(length)]
    return "-".join(residues)


def motif_match_score(sequence: str, motifs: list[str]) -> float:
    residues = sequence.replace("-", "")
    if not motifs:
        return 0.0
    hits = sum(1 for motif in motifs if motif in residues)
    return round(hits / len(motifs), 3)


def hydrophobicity_index(sequence: str) -> float:
    residues = sequence.replace("-", "")
    if not residues:
        return 0.0
    hydrophobic_count = sum(1 for aa in residues if aa in HYDROPHOBIC)
    return round((hydrophobic_count / len(residues)) * 2 - 1, 3)


def estimate_isoelectric_point(sequence: str) -> float:
    residues = sequence.replace("-", "")
    if not residues:
        return 7.0
    charged = sum(1 for aa in residues if aa in CHARGED)
    bias = (charged / len(residues)) * 3.0
    return round(5.5 + bias, 2)


def estimate_synthesizability(sequence: str) -> float:
    residues = sequence.replace("-", "")
    complexity_bonus = len(set(residues)) / max(len(residues), 1)
    cysteine_penalty = residues.count("C") * 0.08
    score = 0.55 + complexity_bonus - cysteine_penalty
    return round(max(0.0, min(score, 0.99)), 3)


def simulate_affinity(sequence: str, family: str) -> float:
    residues = sequence.replace("-", "")
    motif_bonus = motif_match_score(sequence, MOTIFS[family]) * -1.8
    hydro_penalty = abs(hydrophobicity_index(sequence)) * 0.9
    length_bonus = -0.04 * min(len(residues), 18)
    noise = random.uniform(-0.6, 0.6)
    return round(-6.0 + motif_bonus - hydro_penalty + length_bonus + noise, 3)


def toxicity_flag(sequence: str) -> bool:
    residues = sequence.replace("-", "")
    return residues.count("C") >= 3 or "WWW" in residues or residues.startswith("KKK")


def dataset_split(index: int, total: int) -> str:
    train_cutoff = int(total * 0.7)
    validation_cutoff = int(total * 0.85)
    if index < train_cutoff:
        return "train"
    if index < validation_cutoff:
        return "validation"
    return "test"


def build_dataset(output_path: str = "baseline_affinities_v1.csv", rows_count: int = 64, seed: int = 42) -> None:
    random.seed(seed)
    rows = []

    for index in range(rows_count):
        family = TARGET_FAMILIES[index % len(TARGET_FAMILIES)]
        sequence = generate_sequence()
        residues = sequence.replace("-", "")
        rows.append(
            {
                "sequence_id": f"SEQ-{index + 1:06d}",
                "sequence_string": sequence,
                "sequence_hash": sequence_hash(sequence),
                "target_family": family,
                "sequence_length": len(residues),
                "motif_match_score": motif_match_score(sequence, MOTIFS[family]),
                "binding_affinity_kcal_mol": simulate_affinity(sequence, family),
                "isoelectric_point": estimate_isoelectric_point(sequence),
                "hydrophobicity_index": hydrophobicity_index(sequence),
                "synthesizability_score": estimate_synthesizability(sequence),
                "toxicity_flag": toxicity_flag(sequence),
                "dataset_split": dataset_split(index, rows_count),
                "source": "synthetic_benchmark_v1",
            }
        )

    output = Path(__file__).with_name(output_path)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    build_dataset()
