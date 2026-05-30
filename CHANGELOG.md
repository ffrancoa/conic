# Changelog

Welcome to the **`conic` changelog**! The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2026-05-30

### Added
- `conic.processing.derivation`: A new submodule dedicated to computing derived parameters from an SCPTu sounding, ranging from corrected cone resistance (`qt`) to Robertson (2016) indices such as `Ic` and `CD`.
- Added `rolling` and `rolling_label` parameters to the `Configurator` class, allowing users to define the window size for calculating rolling averages of `fs` and `qt` utilized by other derived parameters.
- Enabled processing of CPTu sounding results up to normalized indices via `derivation.compute_normalized()`, incorporating the `fs_rol` and `qt_rol` rolling mean averages.

### Changed
- Values replaced by `preparation.clean_by_indicators()` in `replace` mode are now filled with `NaN` instead of `null`. Moving forward, `NaN` will be generally preferred over `null` for numeric columns in future versions.


## [0.2.0] — 2026-05-28

### Added
- `conic.express`: A new module providing a functional paradigm approach to access most common `conic` workflows without interacting directly with the object-oriented API.
- `conic.processing`: Relocated all core CPT/CPTu preprocessing functions into this module.

### Changed
- Renamed `Pipeliner.default()` to `Pipeliner.standard()` for improved semantic consistency.


## [0.1.0] — 2026-05-20

### Added
- `Configurator`: A Pydantic-backed class responsible for managing user-defined configurations, including CPTu test parameters, input/output column mappings, and data-cleaning constraints.
- `Configurator.from_toml()`: Instantiates a `Configurator` instance from TOML files, supporting incremental configuration overrides via fluent `with_*` methods.
- `Pipeliner`: A composable pipeline engine designed to apply sequential, ordered processing steps to a `polars.DataFrame`. Features `Pipeliner.default()` for standard CPTu preprocessing sequences and supports custom step architectures using `StepCatalog`.
- On-demand reproducibility for pipeline runs implemented via `Pipeliner.run(df, metadata=True)`.
- Core CPTu preprocessing functions inside `conic.preprocess`: `compute_hydrostatic`, `adjust_depth_spacing`, `clean_by_indicators`, and `filter_by_indicators`.

[Unreleased]: https://github.com/ferrosoft/reson/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ferrosoft/reson/releases/tag/v0.1.0
[0.2.0]: https://github.com/ferrosoft/reson/releases/tag/v0.2.0
[0.3.0]: https://github.com/ferrosoft/reson/releases/tag/v0.3.0

