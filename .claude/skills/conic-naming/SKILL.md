---
name: conic-naming
description: >
  Naming conventions for conic: functions, variables, parameters,
  columns, modules, and error messages.
---

## Functions

- Processing: `verb_object` (`compute_hydrostatic_column`),
  `verb_by_object` when criterion-driven (`clean_by_indicators`).
- Correlation facades: `add_<tag>_columns` (`add_r21_columns`).
- Expression helpers: `_expr_` prefix, private, return `pl.Expr`.
- Private frame helpers: `_` prefix, no `_expr_`.

## Variables

- Column names (`str`): `col_` prefix (`col_fs`, `col_qt`).
- Column expressions (`pl.Expr`): `_column` suffix
  (`qt_column`, `detrended_qc_column`, `qn_rol_kpa_column`).
- Name after domain meaning, not the operation.
- Brevity where context removes ambiguity: `lazy`, `digits`, `mode`.

## Column Name Literals

All live in `_canonical.py` as `COL_*` constants. Never hardcode
elsewhere. Correlation columns carry provenance: `Su_liq [R21]`.

## Error Messages

Lowercase, no trailing period. Name the offending value/field.
Show rejected value with `!r`. State recovery when possible.

## Parameters (Pure Functions)

Native Python types only. No defaults. `col_*: str` positional
after `lazy`. Config values keyword-only after `*`.

## Modules

- Correlation: `_author_year.py`. Re-exported via `correlations/__init__.py`.
- Private: leading `_`. Public: no underscore.
- Envelope variants use `ENVELOPE_MAP: dict[str, float]` lookup,
  not `match/case`, when all branches map to a float.
