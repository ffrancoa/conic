---
name: conic-polars
description: >
  Polars idioms and constraints for conic: LazyFrame processing,
  expressions, numeric handling. See conic-naming for variable
  conventions, conic-errors for column validation.
---

## Constraints

- All processing on `pl.LazyFrame`. Collect only at pipeline
  boundary (`Pipeliner.run`).
- No Pandas. No row-level iteration (use Rust plugin instead).
- No processing logic in orchestration (`pipeline.py`, `catalog.py`).

## Numeric

- `NaN` over `null` for missing values. `float("nan")` as
  replacement, `fill_nan(None)` to unify before computation.
- Optional numeric params: `is None`, never truthiness.

## Expressions

- `_expr_` helpers: private, stateless, receive column names as
  `str`, return `pl.Expr`. Never receive a `LazyFrame`.
- `pl.selectors` for dtype-wide operations (e.g., indicator
  replacement across all numeric columns).
- Subtree duplication from reusing an expression variable in
  `with_columns` is acceptable.

## Column Access

- Names arrive as `str` params without defaults; catalog supplies
  them. Never hardcode a column string.
- Validation via `check_required_columns` / `has_column` from
  `conic.core._utils` (see conic-errors for details).
