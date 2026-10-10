---
name: conic-rust
description: >
  Rust layer for conic: iterative solvers, Polars plugin bridge,
  CLI binary, maturin build.
---

## When to Use Rust

Only for iterative/coupled kernels needing per-row convergence loops.
If `pl.when/then/otherwise` expresses it, keep it in Python.

## Workspace

Root `Cargo.toml` is a virtual workspace. Crate boundaries follow
consumers and dependencies; domains are modules mirroring Python
(2024 module style: `engine.rs` next to `engine/`, no `mod.rs`).

- `conic-plugins/` (cdylib `_lib`): `src/bridge.rs` declares
  `bridge/engine.rs` and `bridge/tools.rs`, each holding its kwargs
  structs and `#[polars_expr]` fns. Only crate depending on polars,
  pyo3, and serde.
- `conic-plugins/kernels/` (rlib `conic-kernels`, no dependencies):
  `engine/compute_qtn.rs`, `engine/correlate/compute_qc1n.rs`,
  `tools/inverse_filter/compute_qt_inv.rs` plus private stage modules
  (`convolution`, `smoothing`, `interfaces`, `fs_correction`,
  `depth_spacing`; `calc_dz` re-exported from `inverse_filter`). The
  bridge calls into kernels, never the reverse.
- `conic-cli/` (bin, no PyO3): `src/datasets.rs` embeds
  `registry.toml` via `include_str!` and exposes
  `list_datasets(name: Option<&str>)` (no pyo3 bridge).

## CLI Decisions

- Wheel bundling: CI compiles the binary per platform and patches
  `[tool.maturin]` in `pyproject.toml` with `data = "data"` at build
  time (maturin has no `--data` CLI flag). The `data/` dir exists only
  in CI, never in the repo.
- `init` is pure Rust: embeds `workflow/defaults.toml` via
  `include_str!`; `scaffold_config()` truncates at the first
  `[columns.correlation`, so those tables must stay last in
  `defaults.toml`. Scaffolded `pyproject.toml` gets `{version}` from
  `env!("CARGO_PKG_VERSION")`, kept in lockstep with the Python package
  version; `{name}` is the folder basename. Bare `conic init` writes
  only `config.toml` into the cwd.
- clap cannot bind one field to both a positional and `--name`:
  `InitArgs` holds `name_pos` + `name_flag` in a `multiple = false`
  group (not required), resolved `name_flag.or(name_pos)`.
- Colored help/labels reuse clap's re-exported `anstyle` (no extra
  deps): `HELP_STYLES` const wired via `styles = ...` on the root
  command (propagates to subcommands); same `anstyle` powers
  `styled_label` for tty-gated `info:`/`error:` prefixes.

## Python Server (CLI <-> Python IPC)

The CLI never links libpython. Python-side work goes through
`python -m conic._server`: spawned per CLI invocation (NOT a
cross-invocation daemon), newline-delimited JSON over stdio pipes,
shutdown = drop child stdin (EOF) then `wait()`.

- `_server.py` redirects `sys.stdout` to `os.devnull` (responses go
  through the handle saved before the swap) so stray library prints
  cannot corrupt the protocol; heavy imports (polars) stay inside
  handlers so boot is cheap.
- Interpreter lookup order in `PyServer::start`: siblings of the
  canonicalized `current_exe()`, then `$VIRTUAL_ENV`, then PATH.
- Protocol: `{"cmd": ..., ...}` -> `{"status": "ok"}` or
  `{"status": "error", "message": ...}`. Extend the `_handle` dispatch
  for new commands (e.g. `process`).

## Style

- Idiomatic iterators over indexed loops (`iter_mut`, `enumerate`,
  `take`, `skip`).
- `cargo clippy --workspace` clean; `cargo fmt --all --check` passes.
  Root `rustfmt.toml` sets `max_width = 88` (matches ruff); never
  hand-wrap.
- No `#[cfg(test)]` blocks: everything is tested from Python (solvers
  through the plugin interface, CLI through the installed package).
- `//` comments lowercase; `///` doc comments normal capitalization.

## Build

maturin, abi3 wheels, py312 ABI floor (`abi3-py312`).
`extension-module` gated behind the `default` feature so `cargo test`
links without libpython. `pyproject.toml` uses
`manifest-path = "conic-plugins/Cargo.toml"`. Dev: `maturin develop`.

## Plugin Pattern

`#[polars_expr]` fn takes input columns + a serde kwargs struct
(`IterationKwargs`, `InverseFilterKwargs`), processes per row, returns
a Struct unpacked Python-side. One name across the three layers: kernel
file, kernel entry fn and `#[polars_expr]` fn share it, and
`_plugins.py` (package root) registers `<name>_plugin`:
`compute_qtn`, `compute_qc1n`, `compute_qt_inv`.

- `is_elementwise=True` only when each output row depends on its own
  input row alone (`compute_qtn`, `compute_qc1n`); whole-profile
  kernels (`compute_qt_inv`) must be `False`, or the streaming engine
  applies them per batch and returns wrong values without error.
- Inputs may arrive in several chunks: `rechunk()` before
  `cont_slice()`. `cont_slice()` also rejects nulls (missing values
  must be NaN).
- `tests/plugins/test_engines.py` checks streaming == in-memory per
  plugin on a multi-chunk frame; extend it for every new plugin.
- Rust `polars` 0.55 / `pyo3-polars` 0.28 run under Python Polars 2.0;
  no `pyo3-polars` release pairs with 2.0 yet.
