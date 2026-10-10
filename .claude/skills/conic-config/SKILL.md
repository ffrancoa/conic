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

Tools are not part of the `Configurator`: each `tools/<tool>/` owns its
`Config` (numeric parameters, including any `p_ref`) and `Columns`
(input and output names), both following the sub-model pattern
(frozen/slotted, `__post_init__` validation, `from_dict` with
`_validate_keys`). Their defaults reuse the `config/_defaults.py`
constants through `tools/<tool>/_defaults.py`; never duplicate
literals.

## Defaults

`config/defaults.toml` is the canonical source; `config/_defaults.py`
reads it once at import and binds the constants sub-model fields
reference. Keep `defaults.toml` a valid config (a test asserts
`from_toml(defaults.toml) == Configurator()`): schema fields only, omit
`None` optionals. Keep the `[columns.correlation.*]` tables last: the
Rust CLI scaffold truncates the file there. `COL_VS` is dataset-only, a
literal in `_defaults.py`, absent from `defaults.toml`. Tool defaults
in `tools/<tool>/_defaults.py`.
