---
name: conic-datasets
description: >
  Conventions for curating and registering CPTu/SCPTu datasets
  in conic: Parquet schema, metadata, registry, Zenodo publishing.
---

## Registry

`registry.toml` is the single source of truth. Each source:
`citation`, `doi`, `license`, `record`, `reference`. Each
`[sources.<name>.entries.<type>]`: `filename`, `sha256`,
`n_soundings`. The entry key (`cptu`/`scptu`) determines `test_type`
and columns; do not store those in the TOML. `_registry.py` derives
them via `_TEST_TYPES` and exposes `_get_entry(name)` /
`_get_entries(source)`; entry names are `f"{source}_{entry_key}"`.

The same `registry.toml` is embedded at compile time in
`conic-plugins/datasets/` (`include_str!`); keep both consumers in
mind when editing it. `list_datasets` is NOT in the Python API; it
lives only in the Rust CLI (`conic datasets --list`, offline).
`conic datasets --fetch <source>` delegates to the Python server
(see conic-rust), which calls `fetch_dataset`.

## Fetching

https-only URLs; SHA-256 verified (mismatch -> `ValueError`); atomic
write via temp file to content-addressed cache
`root/<sha256>/filename`. Root = `cache_path` arg, else `CONIC_DATA`
env, else `platformdirs.user_cache_dir("conic")/datasets`. Network
failure -> `ConnectionError`.

## Parquet Schema

Canonical column order (on disk):
CPTu -> `Sorted ID`, `Original ID`, [Grouping label], `Area ratio (-)`,
`Depth (m)`, `qc (MPa)`, `fs (kPa)`, `u2 (kPa)`, `u0 (kPa)`,
`σv_tot (kPa)`, `σv_eff (kPa)`. SCPTu appends `Vs (m/s)`.

- `Sorted ID`: dense int 1..N, the `_ID_COL` selection key.
- `Original ID`: source identifier for traceability.
- [Grouping label]: dataset-specific; omit when no meaningful grouping.
- `Area ratio (-)`: per-sounding/location constant, never null.

`DatasetEntry.columns` holds only the processing columns
(`Depth (m)`..`σv_eff (kPa)` [+ `Vs (m/s)`]); the ID columns, grouping
label, and `Area ratio (-)` are excluded.

## API

- `load_dataset(source, test_type="cptu", *, cache_path=None)` ->
  `ConicDataset`; resolves `f"{source.lower()}_{test_type.lower()}"`.
- `fetch_dataset(source, test_type="all", *, cache_path=None)` ->
  pre-fetch one variant or all.
- `ConicDataset.get_sounding(id)`: validates `1..n_soundings`, filters
  by `_ID_COL`, selects `meta.columns`, collects to `DataFrame`.

## Licensing

- "Publicly available" != redistributable; explicit license required.
- DesignSafe: check each dataset's landing page individually.
- Re-hosting derivatives on Zenodo: keep upstream license, attribute
  original authors.
