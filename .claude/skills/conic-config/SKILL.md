---
name: conic-config
description: >
  Configuration system for conic: Configurator, sub-models, TOML
  mapping, defaults, mutation methods.
---

## Structure

`Configurator` (`engine/_configurator.py`): plain `@dataclass` composing
frozen/slotted sub-models `parameters`, `cleansing`, `settings`,
`columns`, plus `tools: dict[str, object]`. Access
`config.parameters.gamma_soil`. `columns` is 3-level:
`.input.depth`, `.output.qt`, `.correlation.r21.kc`.

## Construction

- `Configurator()` -> all defaults.
- `from_dict(data)` -> nested dicts coerced to sub-models.
- `from_toml(path)` -> TOML parsed, routed to `from_dict`.

Every sub-model has `from_dict` running `_validate_keys` (unknown
fields -> `ValueError`). Never bypass `from_dict`.

## Mutation

Sub-models immutable; use `with_*` returning a new `Configurator`.
Internal `_with_field`: `asdict(submodel)` -> merge -> `type(submodel)
.from_dict(merged)` (re-runs `__post_init__`) -> `replace(self, ...)`.
Never `dataclasses.replace` a sub-model directly.

## Tools

Registered into `config.tools` via `with_tool(name, obj)`. A tool may
span multiple keys. `inverse_filter` uses two:
- `with_tool("inverse_filter", Config(...))` -> required; `operation()`
  raises if missing/wrong type.
- `with_tool("inverse_filter_columns", Columns(...))` -> optional output
  names; defaults to `Columns()` when absent.

`Config`/`Columns` are separate dataclasses in `tools/<tool>/_config.py`
and `_columns.py`; `Columns` is NOT nested in `Config`. Register it
separately to rename tool outputs.

## Defaults

Core: module constants in `engine/_defaults.py`, referenced by fields;
mutable ones via `field(default_factory=...)`. Tool defaults in
`tools/<tool>/_defaults.py`.

## Rules

- TOML keys == Python attribute names. No aliases/renaming.
- Value validation in `__post_init__` (`ValueError`).
- Optional numerics: `is None`, never truthiness.
- Two layers only: code defaults + optional user TOML.
