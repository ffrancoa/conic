---
name: conic-rust
description: >
  Rust layer conventions for conic. Use when writing, modifying, or
  reviewing code in _calc.rs, _impl.rs, lib.rs, or the maturin/PyO3
  build configuration.
---

## When to Use Rust

Reserve Rust for iterative or coupled kernels — computations that
require per-row convergence loops or tightly interdependent fields.
Standalone elementwise arithmetic stays in native Polars expressions.

The test: if `pl.when/then/otherwise` or `map_elements` with a
simple closure can express it, it belongs in Python.

## Module Structure

- `_calc.rs`: pure arithmetic (`f64 -> f64`) and convergence logic.
  No Polars dependency, no PyO3 dependency.
- `_impl.rs`: the Polars bridge. `#[polars_expr]` functions, `Series`
  extraction, kwargs deserialization via serde, Struct assembly.
- `lib.rs`: global allocator (`PolarsAllocator`) and `mod`
  declarations. Plugin registration is handled by the
  `#[polars_expr]` proc macro in `_impl.rs`.

Keep the boundary sharp: `_impl.rs` calls into `_calc.rs`, never
the reverse.

## Build

Mixed Python+Rust via maturin. abi3 wheels with py312 ABI floor.
The `extension-module` feature is gated behind `default` so
`cargo test` can link without `libpython`.

## Testing

No Rust-side tests. All Rust logic is tested from the Python layer
through the plugin interface. This keeps the test suite unified and
avoids the overhead of maintaining a parallel Rust test harness
with mock data.

## Plugin Pattern

A `#[polars_expr]` function takes input columns plus kwargs
(deserialized from the Python side), processes per row, and
returns a Polars Struct that gets unpacked on the Python side.
Python-side registration lives in `core/_plugins.py`.

## Naming

Follow standard Rust conventions. The plugin name exposed via
`#[polars_expr]` matches the Python-side operation it backs:
`compute_behavior` in Rust corresponds to
`compute_behavior_columns` in the catalog.

