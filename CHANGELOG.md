# Changelog

Welcome to the **`conic` changelog**! The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.5] — 2026-07-02

### Added
- `conic` CLI binary (pure Rust, ships inside the wheel); supports `--help` and `--version` for now
- Rust workspace restructured into `conic-plugins/` (cdylib bridge) with `processing/`, `correlations/`, and `tools/` sub-crates (rlibs); Rust source no longer lives alongside Python in `src/`

### Changed
- Root `Cargo.toml` is now a virtual workspace; the Polars plugin cdylib moved to `conic-plugins/Cargo.toml` via maturin `manifest-path`
- CI release workflow compiles the CLI binary per platform and bundles it into the wheel via maturin `data/scripts/`

## [0.6.4] — 2026-06-29

### Added
- `conic.core.correlations`: Boulanger & Idriss (2014) correlation for fines content, stress-normalized tip resistance (qc1N), and clean-sand equivalent (qc1Ncs) via iterative convergence; exposed as `add_bi14_columns()` and wired into the catalog and standard pipeline
- Sleeve friction alignment via `align_sleeve_column()`, which estimates the optimal lag between qc and fs by cross-correlating detrended signals and shifts fs accordingly
- `floor_input_columns()` guard step that replaces zero-valued input columns (qc, fs, and sv_eff when present) with a small fraction of the reference pressure to prevent division-by-zero in downstream normalizations
- Canterbury and Nisqually open CPTu datasets in `conic.datasets`
- Docstrings (NumPy style) for all public functions in `conic.express`

### Changed
- Renamed `conic.core.correlate` module to `conic.core.correlations`; the public re-exports remain the same
- Renamed `process_std()` to `process_standard()` in `conic.express`
- Correlation output column names now live in `_canonical.py` and flow through `Configurator` via `config.columns.correlation.<tag>` (nested `BI14Columns`, `R21Columns`, `OS02Columns` dataclasses in `config.py`); they are no longer hardcoded in each correlation module
- Unified column validation across `conic.core`: all modules now use `check_required_columns()` and `has_column()` from `conic.core._utils` instead of ad-hoc patterns
- Correlation functions use a pipe-based composition pattern instead of `pl.concat` for chaining LazyFrame operations
- `SourceMetadata` dataclass in `conic.datasets` now centralizes citation, DOI, license, and Zenodo record fields per source, replacing the previous flat metadata layout
- Updated `polars` to [`1.42.0`](https://github.com/pola-rs/polars/releases/tag/py-1.42.0)

## [0.6.3] — 2026-06-23

### Added
- `conic.datasets`: a new module to pull open CPT datasets straight from public Zenodo records. `load_dataset()` returns a `ConicDataset` that bundles the lazy data with its metadata and exposes `get_sounding(id)`; `fetch_dataset()` pre-downloads one or every variant into a local cache; and `list_datasets()` prints the available catalog. Ships the Premstaller (CPTu + SCPTu) and Tailings (CPTu) datasets, cached content-addressed with SHA-256 integrity checks.
- `conic.express.read_excel()` to load a sounding from an Excel workbook (selecting the sheet by number or name) into a ready-to-process DataFrame.

### Changed
- `Configurator` and its sub-models are now plain Python dataclasses instead of Pydantic models — the Pydantic dependency is gone and import/startup time drops noticeably. Build from dicts with `Configurator.from_dict()`, snapshot with `.to_dict()`, and note that invalid values now raise a plain `ValueError`.
- Minimum supported Python is back to `3.12` (0.6.0 had raised it to `3.14`); nothing in the library requires a newer interpreter.
- Updated the Rust build stack to `polars` `0.54.4`, `pyo3` `0.28`, and `pyo3-polars` `0.27`.

### Removed
- On-demand run metadata: `Pipeliner.run()` now returns a `polars.DataFrame` directly (the `metadata=` flag and the `PipelineResult` return type are gone).


## [0.6.0] — 2026-06-07

### Added
- `conic.core.correlate`: a new module bringing empirical liquefaction correlations. For now, it includes Robertson (2021) — clean-sand-equivalent resistance and liquefied undrained strength ratio — and Olson & Stark (2002) — normalized resistance and strength ratio with selectable `mean`/`lower`/`upper` bounds.
- New functional helpers in `conic.express`: `read_csv()` to load a sounding straight into a ready-to-process DataFrame, `build_configurator()` to assemble and override a `Configurator` from a TOML file and/or keyword arguments, and `build_pipeliner()` to compose a custom ordered pipeline.
- `conic.engine.catalog`: a single catalog of pipeline operations (e.g. `add_r21_columns()`) you can mix and match to build custom pipelines via `build_pipeliner()`.

### Changed
- `Pipeliner.standard()` is now the single standard preset and runs the full CPTu pipeline; whether optional columns are overridden is driven entirely by your `Configurator`.
- `express.process_std()` now has a simpler signature — `process_std(data, config=None, *, metadata=False)`. Build and customize your configuration up front with `build_configurator()`.
- Relocated the core processing functions: the former `conic.processing` now lives under `conic.core` (`core.calculate` for preparation/derivation, `core.correlate` for correlations).
- Minimum supported Python is now `3.14` (previously `3.12`).
- Updated `polars` to [`1.41.2`](https://github.com/pola-rs/polars/releases/tag/py-1.41.2).

### Removed
- The four pipeline presets `Pipeliner.standard_a0/a1/b0/b1()` and the `std_pipeliner="A0".."B1"` argument of `process_std()`. Use `Pipeliner.standard()` for the default flow, or `build_pipeliner()` + `conic.engine.catalog` operations for custom pipelines.


## [0.5.0] — 2026-06-01

### Added
- Introduced `conic.express.process_std` to replace the old `express.process()` function. This update gives you the flexibility to easily choose between four brand-new standard pipeline configurations.
- Added four new default pipeline presets via `Pipeliner.standard_*()`. You can now use "A" for a partial CPTu pipeline run or "B" for a full pipeline. Additionally, you can append "0" or "1" modifiers to effortlessly control whether optional columns in your original DataFrame should be overridden.
- Finally, the Rust plugin to compute derivated CPTu behaviour-based parameters was implemented via `processing.compute_behavior()`.

### Changed
- Standardized all error messages to consistently start with a lowercase letter.


## [0.4.0] — 2026-05-30

### Changed
- Updated `polars` to version [`1.41.2`](https://github.com/pola-rs/polars/releases/tag/py-1.41.2).
- Migrated all core processing functions from eager `DataFrame` to `LazyFrame` execution. As a breaking change, future execution of processing methods now strictly requires the use of the `Pipeliner` and `StepCatalog` APIs.
- Slightly optimized the performance across multiple core processing operations.

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

[Unreleased]: https://github.com/ferrosoft/conic/compare/v0.6.5...HEAD
[0.6.5]: https://github.com/ferrosoft/conic/compare/v0.6.4...v0.6.5
[0.6.4]: https://github.com/ferrosoft/conic/compare/v0.6.3...v0.6.4
[0.1.0]: https://github.com/ferrosoft/conic/releases/tag/v0.1.0
[0.2.0]: https://github.com/ferrosoft/conic/releases/tag/v0.2.0
[0.3.0]: https://github.com/ferrosoft/conic/releases/tag/v0.3.0
[0.4.0]: https://github.com/ferrosoft/conic/releases/tag/v0.4.0
[0.5.0]: https://github.com/ferrosoft/conic/releases/tag/v0.5.0
[0.6.0]: https://github.com/ferrosoft/conic/releases/tag/v0.6.0
[0.6.3]: https://github.com/ferrosoft/conic/releases/tag/v0.6.3
