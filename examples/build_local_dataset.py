from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from datasets.build_benchmark_datasets import build_dataset


if __name__ == "__main__":
    build_dataset(rows_count=128)
