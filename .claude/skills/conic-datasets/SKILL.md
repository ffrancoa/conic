---
name: conic-datasets
description: >
  Conventions for curating, publishing, and registering CPTu/SCPTu
  datasets in conic. Use when building a new dataset Parquet,
  updating an existing one, writing _metadata.py / _registry.py
  entries, or preparing a Zenodo upload.
---

## Module Layout

- `conic/datasets/_metadata.py`: `SourceMetadata` frozen dataclass
  and one instance per source (e.g., `PREMSTALLER`, `TAILINGS`).
- `conic/datasets/_registry.py`: `DatasetEntry` frozen dataclass
  composing a `SourceMetadata`; URL derived from
  `source.record` + `filename`. Entries keyed by
  `"{source}_{test_type}"` (e.g. `premstaller_cptu`).
- `conic/datasets/_fetch.py`: download, SHA-256 verify, atomic
  write to content-addressed cache (`root/<sha256>/filename`).
- `conic/datasets/_dataset.py`: `ConicDataset` with `meta`,
  `data` (LazyFrame), `__len__`, `get_sounding(id)`.
- `conic/datasets/__init__.py`: eagerly imports `ConicDataset`,
  `fetch_dataset`, `load_dataset`, `DatasetEntry`, `list_datasets`.

## Schema Conventions

Every curated Parquet follows a canonical column order.

- For CPTu: `Sorted ID`, `Original ID`, [Grouping label], `Area ratio (-)`, `Depth (m)`, `qc (MPa)`,
`fs (kPa)`, `u2 (kPa)`, `u0 (kPa)`, `σv_tot (kPa)`, `σv_eff (kPa)`.

- SCPTu adds `Vs (m/s)` at the end.

Rules:
- `Sorted ID`: dense int 1..N per file; the selection
  key for `load_dataset` / `get_sounding`.
- `Original ID`: source identifier, when available, for traceability only.
- [Grouping label] (e.g., `Location`, `Site name`, `Ore`): dataset-specific;
  omitted when there is no meaningful grouping.
- `Area ratio (-)`: per-sounding or per-Location constant; never
  null.

## _metadata.py / _registry.py

`SourceMetadata` fields: `citation`, `doi` (source DOI, not
Zenodo), `license`, `record` (Zenodo version record id),
`reference` (short form), `id_col` (default `"Sorted ID"`).

`DatasetEntry` fields: `name`, `filename`, `sha256`, `test_type`,
`n_soundings`, `columns` (tuple of data columns only — excludes
sounding key, Original ID, and grouping label), `source` (a
`SourceMetadata`). `url` is a `@property` derived from
`source.record` + `filename`; it is not a constructor argument.

`load_dataset(source, test_type)` returns a `ConicDataset`.
Per-sounding access is via `ConicDataset.get_sounding(id)`, which
filters by `id_col == id`, selects `entry.columns`, and collects
to a `DataFrame`.

`fetch_dataset(source, test_type)` downloads entries to the
content-addressed cache without loading them. Useful for
pre-fetching before offline use.

## Licensing Rules

- "Publicly available" ≠ redistributable. The right to
  redistribute must come from an explicit license (CC BY,
  ODC-By, CC0, etc.) on the specific copy you take.
- DesignSafe assigns a license per publication; developer must
  check each dataset's landing page individually.
- Never license data you do not own. When re-hosting a
  derivative on Zenodo, maintain the upstream license and
  attribute the original authors.

