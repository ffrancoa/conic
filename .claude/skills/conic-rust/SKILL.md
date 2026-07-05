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

- `conic-cli/` (bin): pure Rust CLI binary. Uses clap, indicatif,
  serde_json. No PyO3 dependency. CI compiles it per-platform and
  passes `--data data` to maturin so the binary is included in the
  wheel (the `data/` dir is created only in CI, not in the repo).
  `datasets --list` reads the embedded `registry.toml` (offline, no
  Python). `datasets --fetch <source>` drives the Python server
  (see below).
- `conic-plugins/` (cdylib): Polars plugin bridge.
  - `src/lib.rs`: `PolarsAllocator`, `mod` declarations.
  - `src/bridge.rs`: `#[polars_expr]` fns, Series extraction,
    kwargs via serde (`IterationKwargs`), Struct assembly.
  - `processing/` (rlib): Robertson 2016 solver (n, Qtn, Ic).
  - `correlations/` (rlib): Boulanger & Idriss 2014 solver (qc1Ncs).
  - `tools/` (rlib): inverse filter solver (Boulanger & DeJong 2018).
    Depends on `conic-processing` for `calc_qtn`/`calc_ic`/`calc_n`.
  - `datasets/` (rlib): parses `registry.toml` (embedded via
    `include_str!`) with `serde`/`toml`/`regex`. Exposes
    `list_datasets()`. Consumed by `conic-cli` only; no pyo3 bridge.

Boundary: `bridge.rs` calls into the three rlib crates, never reverse.

## Python Server (CLI <-> Python IPC)

For work that must run in Python without linking libpython (keeps the
CLI a standalone binary that ships in the wheel), `conic-cli` spawns a
Python server on demand and talks to it over stdio pipes.

- Python side: `src/conic/_server.py`, run via `python -m conic._server`.
  Reads newline-delimited JSON requests from stdin, dispatches by `cmd`,
  writes one JSON response per line to stdout. It reassigns
  `sys.stdout = sys.stderr` so stray library prints can't corrupt the
  protocol stream, and imports heavy deps (polars) lazily inside the
  handler so server boot stays cheap.
- Rust side (`main.rs`): `PyServer` locates the interpreter
  (`python3`/`python` sibling of the canonicalized `current_exe()`,
  else PATH), spawns it, and does line-framed request/response via
  `serde_json`. Shutdown = drop child stdin (EOF) then `wait()`.
- Lifecycle: server per CLI invocation (spawned on demand, handles N
  requests, closed at exit). NOT a cross-invocation daemon.
- Protocol: `{"cmd": "fetch", "source": ...}` ->
  `{"status": "ok"}` or `{"status": "error", "message": ...}`.
  Extend the `_handle` dispatch with new `cmd`s (e.g. `process`).

## Style

Prefer idiomatic iterators over indexed loops. Use `.iter_mut()`,
`.enumerate()`, `.take()`, `.skip()` instead of `for i in 0..n`
with manual indexing. Run `cargo clippy --workspace` and fix all
warnings before finishing.

No `#[cfg(test)]` blocks in the Rust crates; tests live on the Python
side. Non-doc comments (`//`) are lowercase; doc comments (`///`) keep
normal capitalization.

Formatting: root `rustfmt.toml` sets `max_width = 88` (the Rust analog
of ruff's line length in `pyproject.toml`). Run `cargo fmt --all` (or
rely on rust-analyzer format-on-save, which reads the same file); never
hardcode wrapping. `cargo fmt --all --check` must pass.

CLI help is colored via a `clap::builder::styling::Styles` const
(`HELP_STYLES` in `main.rs`) wired with `styles = HELP_STYLES` on the
root `#[command(...)]`; clap propagates it to subcommands. No extra
deps: reuses clap's re-exported `anstyle`, tty-gated by clap's default
`color` feature (honors `NO_COLOR`/`--color`). Same `anstyle` powers
`styled_label` for `info:`/`error:` prefixes.

## Build

Mixed Python+Rust via maturin; abi3 wheels, py312 ABI floor
(`abi3-py312`). `extension-module` gated behind `default` feature so
`cargo test` links without `libpython`. Dev: `maturin develop` (debug);
CI does `--release` for PyPI. `pyproject.toml` uses
`manifest-path = "conic-plugins/Cargo.toml"`.

## Testing

No Rust-side tests. Everything is tested from Python: solvers through
the plugin interface, datasets/CLI through the installed package.

## Plugin Pattern

`#[polars_expr]` takes input columns + kwargs, processes per row,
returns a Struct unpacked Python-side. Register in `_plugins.py`
(package root). Naming `<rust>` -> `<rust>_plugin`: `compute_qtn` ->
`compute_qtn_plugin`, `compute_qc1n` -> `compute_qc1n_plugin`,
`inverse_filter` -> `inverse_filter_plugin`.
