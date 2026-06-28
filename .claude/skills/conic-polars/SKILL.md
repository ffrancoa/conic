---
name: conic-polars
description: >
  Polars idioms and constraints specific to conic. Use when writing,
  modifying, or reviewing data processing logic — expressions,
  LazyFrame pipelines, column operations, or numeric handling.
---

## Core Constraints

- All processing on `pl.LazyFrame`. Collection only at the pipeline
  boundary (`Pipeliner.run`), never inside a processing function.
- No Pandas. No conversion, no interop, no fallback.
- No row-level iteration. If a per-row loop seems necessary, it
  belongs in Rust via the plugin bridge.
- No processing logic in the orchestration layer (`pipeline.py`,
  `catalog.py`).

## Numeric Conventions

- `NaN` over `null` for missing or replaced numeric values.
  `float("nan")` as replacement, `fill_nan(None)` to unify
  before computation.
- Optional numeric parameters: always `is None`, never truthiness.
  `0.0` is falsy but valid.

## Expression Helpers

- Prefix `_expr_`. Private, stateless, return `pl.Expr`.
- Receive column names as `str`, never a `LazyFrame`.
- Name intermediates after domain meaning, not the Polars
  operation: `detrended_qc_column`, not `rolling_subtracted`.

## Column Access

- Names arrive as `str` parameters defaulting to `_canonical.py`
  constants. Never hardcode a column string.
- Schema inspection via `get_column_names` / `get_missing_columns`
  (no collection).
- Use `pl.selectors` for uniform dtype-wide operations (e.g.,
  indicator replacement across all numeric columns).

## Expression Reuse

Subtree duplication from reusing an expression variable in
`with_columns` is acceptable. Prefer clarity over manual
deduplication.

