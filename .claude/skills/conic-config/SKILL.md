---
name: conic-config
description: >
  Configuration system for conic: Configurator, sub-models, TOML
  mapping, defaults, mutation methods.
---

## Rules

- `Configurator` is a plain `@dataclass`; sub-models frozen/slotted.
  `columns` is 3-level: `.input.depth`, `.output.qt`,
  `.correlation.r21.kc`.
- Never bypass `from_dict`: it runs `_validate_keys` on every sub-model
  (unknown keys -> `ValueError`).
- Mutate only via `with_*` methods built on `_with_field`
  (`asdict` -> merge -> `from_dict` -> `replace`). Never
  `dataclasses.replace` a sub-model directly: it skips
  `__post_init__`.
- TOML keys == Python attribute names. No aliases/renaming.
- Value validation in `__post_init__` (`ValueError`).
- Optional numerics: `is None`, never truthiness.
- Two layers only: code defaults + optional user TOML.

## Tools

Register via `with_tool(name, obj)` into `config.tools`. A tool may
span multiple keys: `inverse_filter` requires a `Config`;
`inverse_filter_columns` optionally renames outputs (defaults to
`Columns()` when absent). `Columns` is NOT nested in `Config`; register
it separately.

## Defaults

`config/defaults.toml` is the canonical source; `config/_defaults.py`
reads it once at import and binds the constants sub-model fields
reference. Keep `defaults.toml` a valid config (a test asserts
`from_toml(defaults.toml) == Configurator()`): schema fields only, omit
`None` optionals. Keep the `[columns.correlation.*]` tables last: the
Rust CLI scaffold truncates the file there. `COL_VS` is dataset-only, a
literal in `_defaults.py`, absent from `defaults.toml`. Tool defaults
in `tools/<tool>/_defaults.py`.
