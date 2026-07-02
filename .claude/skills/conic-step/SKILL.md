---
name: conic-step
description: >
  Step/Operation/bind architecture, catalog factories, and pipeline
  assembly in conic.
---

## Core Types (all in `engine/_pipeliner.py`)

- **Step**: `name` + `apply: LazyFrame -> LazyFrame`, closed over params.
- **Operation**: wraps `build: Configurator -> Step`. Deferred binding.
- **bind(fn, /, **kwargs)**: closes a pure fn over kwargs; `name` from
  `fn.__name__`. Returns `Step`.

Lifecycle: `Operation.build(config)` -> `bind(fn, **kwargs)`.

## Locations

- Pure fns: `processing/` or `correlations/`. No engine imports.
- Catalog factories: `catalog/{_prepare,_derive,_correlations}.py`.
  User import: `from conic import catalog`.
- Pipeline assembly: `engine/_pipeliner.py` `_standard_ops()`.
- Tool ops: `tools/<tool>/_operation.py`.

No processing logic in catalog or pipeliner.

## Catalog Factory

Takes optional step-level overrides, returns `Operation`. Inside
`build(config)`: read from `config.parameters/.cleansing/.settings/
.columns` (`input`/`output`/`correlation.<tag>`) using names
`input_columns`, `output_columns`, `correlation_columns`; then
`return bind(pure_fn, **kwargs)`. Conditional ops check a config flag
and return a no-op `Step(name=..., apply=lambda lazy: lazy)`.

## Tool Operation

Autonomous subpackage `tools/<tool>/` owning `_config.py`, `_columns.py`,
`_defaults.py`, `_compute.py`, `_operation.py`. `_operation.py` exposes
`operation() -> Operation`. Inside `build`: `config.tools.get("<tool>")`,
raise `ValueError` if None and `TypeError` if not the expected `Config`;
read optional `config.tools.get("<tool>_columns", Columns())` (also type
-checked); then `bind`.

## Pure Function Signatures

`lazy: pl.LazyFrame` first, then positional `col_*: str` (no defaults),
then keyword-only config values after `*` (no defaults). Returns
`pl.LazyFrame`.

## Pipeliner

Frozen dataclass. `Pipeliner.standard(config)` builds from
`_standard_ops()`; `.run(data) -> DataFrame` lazies input, applies
steps, collects. Input validation implicit via `filter_input_columns`
(first standard step).

## Adding a Standard Op

1. Pure fn in `processing/`. 2. Factory in `catalog/_prepare.py` or
`catalog/_derive.py`. 3. Insert `Operation` at correct position in
`_standard_ops()`. 4. Add defaults to `engine/_defaults.py` + fields to
`engine/_configurator.py` if needed.

## Adding a Tool Op

1. Create `tools/<tool>/` subpackage (files above). 2. Register
`with_tool("<tool>", Config(...))` (+ optional `"<tool>_columns"`).
3. Append `<tool>.operation()` to the pipeline steps.
