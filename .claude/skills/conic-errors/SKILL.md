---
name: conic-errors
description: >
  Error handling conventions for conic. Use when writing, modifying,
  or reviewing error raising, exception types, or validation logic.
---

## Exception Types

- `ColumnNotFoundError` (from `polars.exceptions`): missing columns
  in a DataFrame.
- `ValueError`: invalid configuration values, invalid arguments,
  or violated preconditions.

No custom exception classes unless a genuinely distinct failure
mode demands one.

## Message Style

Messages start lowercase, read as direct statements to a
geotechnical engineer, and name the offending value or field:

```
"depth column is missing in DataFrame: 'z'"
"invalid max offset -5; value must be a positive integer"
"a valid soil unit weight value (`gamma_soil`) must be provided to compute geostatic stresses"
"hydrostatic pressure ('u0') was already included in this DataFrame; set `override=True` to override"
"invalid `action` argument; use only 'replace' or 'remove'"
```

Patterns to follow:
- Identify what is wrong and where: `"missing required columns: '{columns}'"`.
- When a value is invalid, show the rejected value: `f"invalid max offset {max_offset!r}"`.
- When recovery is possible, state how: `"set `override=True` to override"`.
- Use `repr` (`!r`) for values, single quotes for column or field names.

## Avoid

- `print` + `return None` as error signaling.
- Bare `Exception` or `RuntimeError` where a specific type fits.
- Uppercase or sentence-case messages (`"Missing columns"`,
  `"Invalid value for..."`).
- Generic messages that hide the cause: `"something went wrong"`,
  `"invalid input"`.
- Swallowing exceptions silently or converting them to warnings.

