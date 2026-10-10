---
name: conic-naming
description: >
  Naming conventions for conic: functions, variables, parameters,
  columns, modules, and error messages.
---

## Functions

- Processing: `verb_object` (`compute_hydrostatic_column`);
  `verb_by_object` when criterion-driven (`clean_by_indicators`).
- Correlation facades: `add_<tag>_columns` (`add_r21_columns`).
- Expression helpers: `_expr_` prefix, private, return `pl.Expr`.
- Private frame helpers: `_` prefix, no `_expr_`.

## Variables

- Column names (`str`): `col_` prefix (`col_fs`, `col_qt`).
- Column expressions (`pl.Expr`): `_column` suffix (`qt_column`,
  `qn_rol_kpa_column`).
- Name after domain meaning, not the operation. Be terse where context
  disambiguates (`lazy`, `digits`, `mode`).

## Column Literals

Core columns: `COL_*` constants in `workflow/_defaults.py` (bound from
`defaults.toml` at import; correlation tables as `CORR_*`). Tool columns: `tools/<tool>/_defaults.py`.
Never hardcode elsewhere; transient scratch columns (`COL_TEMP =
"_temp"`) are the only exception. Correlation columns carry provenance:
`Su_liq (-) [R21]`.

## Parameters (Pure Functions)

Native Python types. `col_*: str` positional after `lazy`; config
values keyword-only after `*`. Configurator-sourced kwargs take no
defaults; step-level toggles may (`override=False`, `digits=3`,
`indicators=None`).

## Modules

- Correlation: `_author_year.py` (`_olson2002.py`), re-exported via
  `engine/correlate/__init__.py`.
- Private: leading `_`. Public: no underscore.
- Envelope variants: `ENVELOPE_MAP: dict[str, float]` lookup, not
  `match/case`, when all branches map to a float.

## Error Messages

Lowercase, no trailing period; name the offending value/field; show it
with `!r`; state recovery. See conic-errors.
