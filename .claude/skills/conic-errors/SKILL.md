---
name: conic-errors
description: >
  Error handling and column validation for conic. Exception types,
  validation functions, message formatting.
---

## Exception Types

- `ColumnNotFoundError` (from `polars.exceptions`): missing columns.
  Never import or raise directly; use `check_required_columns`.
- `ValueError`: invalid config, arguments, or preconditions.
- No custom exceptions unless a distinct failure mode demands one.

## Column Validation (`conic.core._utils`)

- `check_required_columns(lazy, {col_a, col_b})`: raises
  `ColumnNotFoundError` if any missing. For mandatory preconditions.
- `has_column(lazy, col)`: returns `bool`. For conditionally
  present columns (e.g., `sv_eff` before geostatic computation).

No other validation pattern. Do not import `ColumnNotFoundError`
directly in `conic.core` modules.

## Message Style

Lowercase, no trailing period. Name the offending value/field.

```
"missing required columns: {missing}"
"invalid envelope choice, valid options are {opts}; got {v!r}"
"set `override=True` to override"
```

- Show rejected value with `!r`, column/field names in single quotes.
- State recovery path when possible.

## Avoid

- `print` + `return None` as error signaling.
- Bare `Exception`/`RuntimeError`.
- Uppercase/sentence-case messages.
- Generic messages hiding the cause.
- Swallowing exceptions or converting to warnings.
