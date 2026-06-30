---
name: conic-rust
description: >
  Rust layer for conic: iterative solvers, Polars plugin bridge,
  maturin build.
---

## When to Use Rust

Only for iterative/coupled kernels needing per-row convergence loops.
If `pl.when/then/otherwise` can express it, keep it in Python.

## Module Structure

- `_calc.rs`: Robertson 2016 solver (n, Qtn, Ic). Pure arithmetic.
- `_corr.rs`: Boulanger & Idriss 2014 solver (qc1Ncs). Pure arithmetic.
- `_impl.rs`: Polars bridge. `#[polars_expr]` functions, Series
  extraction, kwargs via serde (`IterationKwargs`), Struct assembly.
- `lib.rs`: `PolarsAllocator`, `mod` declarations.

Boundary: `_impl.rs` calls into `_calc.rs`/`_corr.rs`, never reverse.

## Build

Mixed Python+Rust via maturin. abi3 wheels, py312 ABI floor.
`extension-module` gated behind `default` so `cargo test` links
without `libpython`.

Development: `maturin develop` (debug mode). No `--release` locally.
CI handles `--release` for PyPI.

## Testing

No Rust-side tests. All tested from Python through the plugin
interface.

## Plugin Pattern

`#[polars_expr]` takes input columns + kwargs, processes per row,
returns Polars Struct unpacked on Python side. Registration in
`core/_plugins.py`.

Naming: `compute_qtn` (Rust) -> `compute_qtn_plugin` (Python).
`compute_qc1n` -> `compute_qc1n_plugin`.
