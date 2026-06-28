---
name: conic-naming
description: >
  Naming conventions for the conic codebase. Use when writing, renaming,
  or reviewing Python code in conic — functions, variables,
  parameters, columns, modules, and correlation artifacts.
---

## Functions

Use generous, descriptive names that read as technical prose.
Never abbreviate at the cost of clarity.

- Pure processing functions: `verb_object` when unconditional,
  `verb_by_object` when a criterion selects behavior.
  Examples: `adjust_depth_spacing`, `clean_by_indicators`,
  `compute_hydrostatic_column`.

- Correlation factories: `add_<tag>_columns` where `<tag>` is a
  lowercase author-year code. Example: `add_r21_columns`,
  `add_os02_columns`.

- Expression-returning helpers: prefix `_expr_`.
  Example: `_expr_estimate_sleeve_offset`, `_expr_estimate_mean_spacing`.

- Private helpers that operate on frames: prefix `_`, no `_expr_`.
  Example: `_remove_rows_with_indicators`.

## Variables and Parameters

Names reflect what the value represents in the domain, not the
operation that produced it.

Good: `detrended_qc_column`, `pearson_correlations`,
`max_correlation_index`, `sleeve_offset`, `global_mask`,
`cleaned_fs_column`.

Bad: `rolling_subtracted`, `corr_list`, `idx`, `result`, `temp`.

Brevity is acceptable where context already removes ambiguity:
`lazy` (not `lazy_frame`), `col_depth` (not `column_depth`),
`digits` (not `rounding_digits`), `mode` (not `clean_mode_string`).

The test: could someone reading only the name infer what the variable
holds without checking the assignment?

## Column Names

All column-name literals live exclusively in `_canonical.py` as
module-level constants prefixed `COL_`. Never hardcode a column
string anywhere else.

Correlation output columns carry an author-year provenance tag:
`Su_liq [R21]`, `qc1 [OS02]`.

## Parameters in Pure Functions

Use native Python types (`float`, `str`, `int`, `list[float]`), never
config or validation types. Defaults come from `_canonical.py`
constants.

Column-name parameters: prefix `col_`. Example: `col_depth`, `col_qc`,
`col_fs`, `col_u2`.

## Modules

- Correlation modules: `_author_year.py`. Example: `_robertson2021.py`,
  `_olson2002.py`.
- Private modules: leading underscore. Example: `_canonical.py`,
  `_plugins.py`, `_utils.py`.
- Public modules: no underscore. Example: `config.py`, `catalog.py`,
  `pipeline.py`.
- Correlation composition module: `compose.py` in `core/correlate/`.
  Contains the public `add_<tag>_columns` functions that wire
  private correlation modules together.

