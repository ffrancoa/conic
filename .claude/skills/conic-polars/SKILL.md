---
name: conic-polars
description: >
  Polars idioms and constraints for conic: LazyFrame processing,
  expressions, numeric handling. See conic-naming for variable
  conventions, conic-errors for column validation.
---

## Constraints

- All processing on `pl.LazyFrame`. Collect only at the pipeline
  boundary (`Pipeliner.run`).
- No Pandas. No row-level iteration (use the Rust plugin).
- No processing logic in orchestration (`pipeline/_core.py`,
  `catalog/`).

## Numeric

- `NaN` over `null` for missing values: `float("nan")` to replace,
  `fill_nan(None)` to unify before computing, `fill_null(float("nan"))`
  after window ops that introduce nulls.
- Optional numeric params: `is None`, never truthiness.

## Expressions

- `_expr_` helpers: private, stateless, return `pl.Expr`, never receive
  a `LazyFrame`. Params are column names (`str`) or `pl.Expr`.
- Chain multi-stage transforms with `.pipe()`, not intermediate frames.
- `pl.selectors` for dtype-wide ops (e.g. indicator replacement across
  numeric columns).
- Subtree duplication from reusing an expression var in `with_columns`
  is acceptable.
- Hand-aligned `with_columns` blocks end with `)  # fmt: off`.

## Column Access

- Names arrive as `str` params without defaults; catalog supplies them.
  Never hardcode a column string.
- Validate via `check_required_columns` / `has_column` from
  `conic._utils` (see conic-errors).
