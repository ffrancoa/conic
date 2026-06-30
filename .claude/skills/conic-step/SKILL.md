---
name: conic-step
description: >
  Step/Operation/bind architecture, catalog factories, and pipeline
  assembly in conic.
---

## Core Types (all frozen dataclasses in `engine/step.py`)

- **Step**: `name` + `apply: LazyFrame -> LazyFrame`, closed over params.
- **Operation**: wraps `build: Configurator -> Step`. Deferred binding.
- **bind(fn, **kwargs)**: closes a pure function over kwargs, derives
  `name` from `fn.__name__`. Returns `Step`.

Lifecycle: `Operation.build(config)` -> `bind(function, **kwargs)`.

## File Locations

- Pure functions: `core/calculate/` or `core/correlations/`.
- Catalog factories: `engine/catalog.py`.
- Pipeline assembly: `engine/pipeline.py` (`STANDARD_OPS` tuple).

No processing logic in `catalog.py` or `pipeline.py`.

## Catalog Factory Pattern

Factory receives optional step-level overrides, returns `Operation`.
Inside `build(config)`:
1. Extract from `config.parameters`, `.cleansing`, `.settings`,
   `.columns` (input/output/`correlation.<tag>`).
2. Use consistent variable names: `input_columns = config.columns.input`,
   `output_columns = config.columns.output`,
   `correlation_columns = config.columns.correlation.<tag>`.
3. `return bind(pure_function, **kwargs)`.

Conditional ops check a config flag and return no-op `Step` or skip.

## Pure Function Signatures

`lazy: pl.LazyFrame` first, then positional `col_*: str` (no defaults),
then keyword-only config values after `*` (no defaults).
Returns `pl.LazyFrame`. No engine imports.

## Adding a Standard Operation

1. Pure function in `core/`.
2. Catalog factory in `catalog.py`.
3. Insert `Operation` in `STANDARD_OPS` at correct position.
4. Add defaults to `_canonical.py` and fields to `config.py` if needed.

## Pipeliner

Frozen dataclass. `Pipeliner.standard(config)` builds from
`STANDARD_OPS`. `.run(data) -> DataFrame` converts to lazy,
applies steps, collects. Input validation is implicit via
`filter_input_columns` (first standard step).
