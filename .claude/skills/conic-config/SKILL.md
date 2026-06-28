---
name: conic-config
description: >
  Configuration system rules for conic. Use when creating, modifying,
  or reviewing Configurator sub-models, TOML mapping, defaults in
  _canonical.py, or with_* mutation methods.
---

## Architecture

`Configurator` is a plain `@dataclass` (not frozen, not slotted)
that holds no data. It composes four sub-models, all
`@dataclass(frozen=True, slots=True)`: `parameters`, `cleansing`,
`settings`, `columns`.

Access is two levels: `config.parameters.gamma_soil`. The only
exception is `columns`, which has three:
`config.columns.input.depth`, `config.columns.output.qt`.

## Construction

Three entry points, all equivalent in validation guarantees:

- `Configurator()` — all defaults.
- `Configurator.from_dict(data)` — nested dicts coerced to sub-models.
- `Configurator.from_toml(path)` — TOML parsed then routed to
  `from_dict`.

Each sub-model has its own `from_dict` classmethod that rejects
unknown fields via `_validate_keys`. Never bypass `from_dict` to
construct a sub-model from raw `dataclasses.replace` or direct
instantiation with unvalidated data.

## Modification

Immutable by design. All changes go through `with_*` methods, each
returning a new `Configurator` instance.

The internal pattern (`_with_field`):

1. `dataclasses.asdict(submodel)` to get current values.
2. Merge the update: `current | {field: new_value}`.
3. Reconstruct via `type(submodel).from_dict(merged)` — this
   re-runs `__post_init__` validation.
4. `dataclasses.replace(self, submodel_name=new_submodel)`.

Never skip step 3. Using `dataclasses.replace` directly on a
sub-model bypasses `__post_init__` and can produce an invalid
configuration silently.

## Defaults and Constants

All default values live in `_canonical.py` as module-level constants.
Sub-model fields reference these constants as their defaults.
No default value is defined inline in a dataclass field unless it
comes from `_canonical.py`.

Mutable defaults (lists, dicts) use `field(default_factory=...)`.
Never assign a mutable literal as a shared default.

## TOML Mapping

Python attribute names are identical to TOML section and key names.
No aliases, no renaming, no case transformation. What you write in
the TOML file is exactly what you access in Python.

## Validation

Validation lives in `__post_init__` of each sub-model. Rules:

- Unknown keys: rejected by `_validate_keys` in `from_dict`
  before the dataclass is even constructed.
- Invalid values: caught in `__post_init__` with `ValueError`
  identifying the offending field.
- Optional numeric parameters: check with `is None`, never
  truthiness (`if not x` fails on `0.0`).

## Configuration Resolution

Two layers only: code defaults (the dataclass fields) and an
optional TOML file passed explicitly by the user. No automatic
file search, no user-level base config, no deep-merge across
multiple files.
