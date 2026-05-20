# Changelog

Welcome. All notable changes to `conic` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-20

### Added
- `Configurator`: immutable, validated configuration object for CPT processing pipelines. Supports direct construction, TOML file loading via `Configurator.from_toml()`, and incremental modification via `with_*` methods.
- `Pipeliner`: composable pipeline engine that applies ordered processing steps to a `polars.DataFrame`. Includes `Pipeliner.default()` for the standard preprocessing sequence and supports custom step composition via `StepCatalog`.
- Preprocessing functions in `conic.preprocess`: `compute_hydrostatic`, `adjust_depth_spacing`, `clean_by_indicators`, and `filter_by_indicators`.
- Reproducibility metadata returned on demand via `Pipeliner.run(df, metadata=True)`.


[Unreleased]: https://github.com/ferrosoft/reson/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ferrosoft/reson/releases/tag/v0.1.0

