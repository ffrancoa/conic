---
name: conic-datasets
description: >
  Conventions for curating and registering CPTu/SCPTu datasets
  in conic: Parquet schema, metadata, registry, Zenodo publishing.
---

## Module Layout

- `registry.toml`: single source of truth for all dataset metadata.
  Each source has `citation`, `doi`, `license`, `record`, `reference`.
  Each entry under `[sources.<name>.entries.<type>]` has `filename`,
  `sha256`, `n_soundings`. The entry key (`cptu`/`scptu`) determines
  `test_type` and columns; these are not stored in the TOML.
- `_registry.py`: reads `registry.toml` via `tomllib`. Defines
  `SourceMetadata` and `DatasetEntry` dataclasses. Constants
  `_ID_COL`, `_CPTU_COLUMNS`, `_SCPTU_COLUMNS`, `_TEST_TYPES` derive
  test type labels and column tuples from the entry key. `_ENTRIES`
  and `_BY_NAME` are module-level singletons. Lookup via
  `_get_entry(name)` and `_get_entries(source)`.
- `_fetch.py`: https-only download, SHA-256 verify (mismatch ->
  `ValueError`), atomic write via temp file to content-addressed cache
  `root/<sha256>/filename`. Root = `cache_path` arg, else `CONIC_DATA`
  env, else `platformdirs.user_cache_dir("conic")/datasets`. Network
  failure -> `ConnectionError`.
- `_dataset.py`: `ConicDataset(meta, data: LazyFrame)` with `__len__`
  and `get_sounding(id)`.
- `__init__.py` exports: `ConicDataset`, `fetch_dataset`,
  `load_dataset`, `DatasetEntry`, `SourceMetadata`.
  `list_datasets` is NOT in the Python API; it lives only in the
  Rust CLI (`conic datasets --list`).

## Rust Side

The same `registry.toml` is embedded at compile time in
`conic-plugins/datasets/` via `include_str!`. The Rust crate parses
it with `serde`/`toml` and exposes `list_datasets()` for the CLI.
No pyo3 bridge; the crate is consumed only by `conic-cli`.

CLI commands:
- `conic datasets --list`: pure Rust, offline (embedded registry).
- `conic datasets --fetch <source>`: the CLI delegates to the Python
  server (`python -m conic._server`, see conic-rust skill), which calls
  `fetch_dataset` (pure Python). Download logic is unchanged; the CLI
  never links Python.

## Parquet Schema

Canonical column order (on disk):
CPTu -> `Sorted ID`, `Original ID`, [Grouping label], `Area ratio (-)`,
`Depth (m)`, `qc (MPa)`, `fs (kPa)`, `u2 (kPa)`, `u0 (kPa)`,
`σv_tot (kPa)`, `σv_eff (kPa)`. SCPTu appends `Vs (m/s)`.

- `Sorted ID`: dense int 1..N, the `_ID_COL` selection key.
- `Original ID`: source identifier for traceability.
- [Grouping label]: dataset-specific; omit when no meaningful grouping.
- `Area ratio (-)`: per-sounding/location constant, never null.

`DatasetEntry.columns` holds the returned processing columns
(`Depth (m)`..`σv_eff (kPa)` [+ `Vs (m/s)`]) minus the ID columns.

## API

- `load_dataset(source, test_type="cptu", *, cache_path=None)` ->
  `ConicDataset`. Resolves `f"{source.lower()}_{test_type.lower()}"`,
  ensures cache, `scan_parquet`.
- `fetch_dataset(source, test_type="all", *, cache_path=None)` ->
  pre-fetch one variant or all (`"all"`) into cache.
- `ConicDataset.get_sounding(id)`: validates `1..n_soundings`, filters
  by `_ID_COL`, selects `meta.columns`, collects to `DataFrame`.

## Licensing

- "Publicly available" != redistributable; explicit license required.
- DesignSafe: check each dataset's landing page individually.
- Re-hosting derivatives on Zenodo: keep upstream license, attribute
  original authors.
