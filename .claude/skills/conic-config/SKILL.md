---
name: conic-config
description: >
  Configuration system for conic: Configurator, sub-models, TOML
  mapping, defaults, mutation methods.
---

## Architecture

`Configurator` is a plain `@dataclass` composing four frozen/slotted
sub-models: `parameters`, `cleansing`, `settings`, `columns`.

Access: `config.parameters.gamma_soil`. `columns` has three levels:
`config.columns.input.depth`, `config.columns.output.qt`,
`config.columns.correlation.r21.kc`.

## Construction

- `Configurator()`: all defaults.
- `Configurator.from_dict(data)`: nested dicts coerced to sub-models.
- `Configurator.from_toml(path)`: TOML parsed then routed to `from_dict`.

Each sub-model has `from_dict` with `_validate_keys` rejecting
unknown fields. Never bypass `from_dict`.

## Modification

Immutable sub-models. Changes via `with_*` methods returning new
`Configurator`. Internal `_with_field` pattern:
`asdict` -> merge update -> `type(submodel).from_dict(merged)`
(re-runs `__post_init__`) -> `replace(self, ...)`.

Never `dataclasses.replace` directly on a sub-model.

## Defaults

All defaults in `_canonical.py` as module-level constants.
Sub-model fields reference these. Mutable defaults use
`field(default_factory=...)`.

## TOML Mapping

Python attribute names = TOML keys. No aliases, no renaming.

## Validation

- Unknown keys: `_validate_keys` in `from_dict`.
- Invalid values: `__post_init__` with `ValueError`.
- Optional numerics: `is None`, never truthiness.
- Two layers only: code defaults + optional user TOML file.
