---
name: conic-datasets
description: >
  Conventions for curating and registering CPTu/SCPTu datasets
  in conic: Parquet schema, metadata, registry, Zenodo publishing.
---

## Module Layout

- `_metadata.py`: `SourceMetadata` (citation, doi, license, record,
  reference, id_col). One instance per source.
- `_registry.py`: `DatasetEntry` (name, filename, sha256, test_type,
  n_soundings, columns, source). `url` is a `@property` from
  `source.record` + `filename`. Keyed by `"{source}_{test_type}"`.
- `_fetch.py`: download, SHA-256 verify, atomic write to
  content-addressed cache (`root/<sha256>/filename`).
- `_dataset.py`: `ConicDataset` with `meta`, `data` (LazyFrame),
  `__len__`, `get_sounding(id)`.
- `__init__.py`: exports `ConicDataset`, `fetch_dataset`,
  `load_dataset`, `DatasetEntry`, `list_datasets`.

## Parquet Schema

Canonical column order:

CPTu: `Sorted ID`, `Original ID`, [Grouping label], `Area ratio (-)`,
`Depth (m)`, `qc (MPa)`, `fs (kPa)`, `u2 (kPa)`, `u0 (kPa)`,
`σv_tot (kPa)`, `σv_eff (kPa)`.

SCPTu appends `Vs (m/s)`.

- `Sorted ID`: dense int 1..N, the selection key.
- `Original ID`: source identifier for traceability.
- [Grouping label]: dataset-specific, omit when no meaningful grouping.
- `Area ratio (-)`: per-sounding or per-location constant, never null.

## API

- `load_dataset(source, test_type)` -> `ConicDataset`.
- `get_sounding(id)` filters by `id_col`, selects `entry.columns`,
  collects to `DataFrame`.
- `fetch_dataset(source, test_type)` pre-fetches to cache.

## Licensing

- "Publicly available" != redistributable. Explicit license required.
- DesignSafe: check each dataset's landing page individually.
- Re-hosting derivatives on Zenodo: maintain upstream license,
  attribute original authors.
