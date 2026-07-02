---
name: conic-rust
description: >
  Rust layer for conic: iterative solvers, Polars plugin bridge,
  maturin build.
---

## When to Use Rust

Only for iterative/coupled kernels needing per-row convergence loops.
If `pl.when/then/otherwise` expresses it, keep it in Python.

## Modules

- `_calc.rs`: Robertson 2016 solver (n, Qtn, Ic). Pure arithmetic.
- `_corr.rs`: Boulanger & Idriss 2014 solver (qc1Ncs). Pure arithmetic.
- `_filt.rs`: inverse filter solver (Boulanger & DeJong 2018).
- `_impl.rs`: Polars bridge -> `#[polars_expr]` fns, Series extraction,
  kwargs via serde (`IterationKwargs`), Struct assembly.
- `lib.rs`: `PolarsAllocator`, `mod` declarations.

Boundary: `_impl.rs` calls into `_calc`/`_corr`/`_filt`, never reverse.

## Build

Mixed Python+Rust via maturin; abi3 wheels, py312 ABI floor
(`abi3-py312`). `extension-module` gated behind `default` feature so
`cargo test` links without `libpython`. Dev: `maturin develop` (debug);
CI does `--release` for PyPI.

## Testing

No Rust-side tests. All tested from Python through the plugin interface.

## Plugin Pattern

`#[polars_expr]` takes input columns + kwargs, processes per row,
returns a Struct unpacked Python-side. Register in `_plugins.py`
(package root). Naming `<rust>` -> `<rust>_plugin`: `compute_qtn` ->
`compute_qtn_plugin`, `compute_qc1n` -> `compute_qc1n_plugin`,
`inverse_filter` -> `inverse_filter_plugin`.
