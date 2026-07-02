---
name: conic-errors
description: >
  Error handling and column validation for conic. Exception types,
  validation functions, message formatting.
---

## Exceptions

- `ColumnNotFoundError` (`polars.exceptions`): missing columns. Never
  import/raise directly; use `check_required_columns`.
- `ValueError`: invalid config, arguments, or preconditions.
- `TypeError`: wrong runtime type where isinstance is checked (e.g. a
  tool's `Config`/`Columns` in `operation()`).
- No other custom exceptions unless a distinct failure mode demands one.

## Column Validation (`conic._utils`)

- `check_required_columns(lazy, {col_a, col_b})` -> raises
  `ColumnNotFoundError` if any missing. For mandatory preconditions.
- `has_column(lazy, col) -> bool`. For conditionally present columns
  (e.g. `sv_eff` before geostatic computation).

No other validation pattern.

## Message Style

Lowercase, no trailing period. Name the offending value/field; show it
with `!r`; field/column names in single quotes; state recovery when
possible.

```
"missing required columns: {missing}"
"invalid envelope choice, valid options are {opts}; got {v!r}"
"set `override=True` to override"
```

## Avoid

- `print` + `return None` as error signaling.
- Bare `Exception`/`RuntimeError`.
- Uppercase/sentence-case messages; generic messages hiding the cause.
- Swallowing exceptions or converting them to warnings.
