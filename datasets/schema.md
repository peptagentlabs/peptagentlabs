# Dataset Schema

## `baseline_affinities_v1.csv`

| Column | Type | Description |
| --- | --- | --- |
| `sequence_id` | string | Unique identifier such as `SEQ-000001`. |
| `sequence_string` | string | Amino acid sequence using one-letter codes separated by hyphens. |
| `sequence_hash` | string | SHA-256 hash of the sequence string. |
| `target_family` | string | Broad target family such as `benchmark_kinase` or `benchmark_gpcr`. |
| `sequence_length` | integer | Number of residues. |
| `motif_match_score` | float | Score from 0.0 to 1.0 for required motif coverage. |
| `binding_affinity_kcal_mol` | float | Simulated dG score for benchmark use only. |
| `isoelectric_point` | float | Estimated pI. |
| `hydrophobicity_index` | float | Approximate hydrophobicity score. |
| `synthesizability_score` | float | Approximate 0.0 to 1.0 score. |
| `toxicity_flag` | boolean | Heuristic benchmark flag only. |
| `dataset_split` | string | `train`, `validation`, or `test`. |
| `source` | string | `synthetic_benchmark_v1`. |

## `sample_targets_v1.csv`

| Column | Type | Description |
| --- | --- | --- |
| `target_id` | string | PEPTA target identifier. |
| `name` | string | Human-readable target name. |
| `category` | string | Target category such as `benchmark`. |
| `difficulty` | string | `low`, `medium`, or `high`. |
| `min_length` | integer | Minimum sequence length. |
| `max_length` | integer | Maximum sequence length. |
| `required_motifs` | string | Pipe-delimited motif list. |
| `hydrophobicity_min` | float | Lower bound for accepted hydrophobicity. |
| `hydrophobicity_max` | float | Upper bound for accepted hydrophobicity. |
| `reference_source` | string | Synthetic or literature-derived provenance label. |
