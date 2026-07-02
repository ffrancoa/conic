---
name: conic-rust
description: >
  Rust layer for conic: iterative solvers, Polars plugin bridge,
  CLI binary, maturin build.
---

## When to Use Rust

Only for iterative/coupled kernels needing per-row convergence loops.
If `pl.when/then/otherwise` expresses it, keep it in Python.

## Workspace Layout

Root `Cargo.toml` is a virtual workspace with two top-level crates:

- `conic-cli/` (bin): pure Rust CLI binary. Uses clap (with `cargo`
  feature for `crate_version!`/`crate_description!` macros) and
  indicatif. No PyO3 dependency. CI compiles it per-platform and
  places it in `data/scripts/` so maturin includes it in the wheel.
- `conic-plugins/` (cdylib): Polars plugin bridge.
  - `src/lib.rs`: `PolarsAllocator`, `mod` declarations.
  - `src/bridge.rs`: `#[polars_expr]` fns, Series extraction,
    kwargs via serde (`IterationKwargs`), Struct assembly.
  - `processing/` (rlib): Robertson 2016 solver (n, Qtn, Ic).
  - `correlations/` (rlib): Boulanger & Idriss 2014 solver (qc1Ncs).
  - `tools/` (rlib): inverse filter solver (Boulanger & DeJong 2018).
    Depends on `conic-processing` for `calc_qtn`/`calc_ic`/`calc_n`.

Boundary: `bridge.rs` calls into the three rlib crates, never reverse.

## Build

Mixed Python+Rust via maturin; abi3 wheels, py312 ABI floor
(`abi3-py312`). `extension-module` gated behind `default` feature so
`cargo test` links without `libpython`. Dev: `maturin develop` (debug);
CI does `--release` for PyPI. `pyproject.toml` uses
`manifest-path = "conic-plugins/Cargo.toml"`.

## Testing

No Rust-side tests. All tested from Python through the plugin interface.

## Plugin Pattern

`#[polars_expr]` takes input columns + kwargs, processes per row,
returns a Struct unpacked Python-side. Register in `_plugins.py`
(package root). Naming `<rust>` -> `<rust>_plugin`: `compute_qtn` ->
`compute_qtn_plugin`, `compute_qc1n` -> `compute_qc1n_plugin`,
`inverse_filter` -> `inverse_filter_plugin`.
