---
name: conic-datasets
description: >
  Conventions for curating and registering CPTu/SCPTu datasets
  in conic: Parquet schema, metadata, registry, Zenodo publishing.
---

## Module Layout

- `_metadata.py`: `SourceMetadata(citation, doi, license, record,
  reference, id_col="Sorted ID")`, one frozen instance per source.
- `_registry.py`: `DatasetEntry(name, filename, sha256, test_type,
  n_soundings, columns, source)`; `url` is a `@property` building the
  Zenodo URL from `source.record` + `filename`. `ENTRIES` tuple indexed
  by `_BY_NAME` on `entry.name` (`"{source}_{test_type.lower()}"`, e.g.
  `"premstaller_scptu"`). `list_datasets(name=None)` prints the catalog.
- `_fetch.py`: https-only download, SHA-256 verify (mismatch ->
  `ValueError`), atomic write via temp file to content-addressed cache
  `root/<sha256>/filename`. Root = `cache_path` arg, else `CONIC_DATA`
  env, else `platformdirs.user_cache_dir("conic")/datasets`. Network
  failure -> `ConnectionError`.
- `_dataset.py`: `ConicDataset(meta, data: LazyFrame)` with `__len__`
  and `get_sounding(id)`.
- `__init__.py` exports: `ConicDataset`, `fetch_dataset`,
  `load_dataset`, `DatasetEntry`, `list_datasets`.

## Parquet Schema

Canonical column order (on disk):
CPTu -> `Sorted ID`, `Original ID`, [Grouping label], `Area ratio (-)`,
`Depth (m)`, `qc (MPa)`, `fs (kPa)`, `u2 (kPa)`, `u0 (kPa)`,
`σv_tot (kPa)`, `σv_eff (kPa)`. SCPTu appends `Vs (m/s)`.

- `Sorted ID`: dense int 1..N, the `id_col` selection key.
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
  by `source.id_col`, selects `meta.columns`, collects to `DataFrame`.

## Licensing

- "Publicly available" != redistributable; explicit license required.
- DesignSafe: check each dataset's landing page individually.
- Re-hosting derivatives on Zenodo: keep upstream license, attribute
  original authors.
