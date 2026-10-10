---
name: conic-step
description: >
  Step/Operation/bind architecture, catalog factories, and pipeline
  assembly in conic.
---

## Core Types (`workflow/_step.py`)

- **Step**: `name` + `apply: LazyFrame -> LazyFrame`, closed over params.
- **Operation**: wraps `build: Configurator -> Step`. Deferred binding.
- **bind(fn, /, **kwargs)**: closes a pure fn over kwargs; `name` from
  `fn.__name__`. Returns `Step`.

Lifecycle: `Operation.build(config)` -> `bind(fn, **kwargs)`.

## Placement

- Pure fns: `engine/` (incl. `engine/correlate/`). No `workflow` imports.
- Catalog factories: `workflow/catalog/{_clean,_derive,_correlate}.py`
  (mirroring `engine/`), importing `_step` and `_configurator`
  directly, never `workflow/__init__`. User import:
  `from conic import catalog` (lazy re-export in `conic/__init__.py`).
- Pipeline assembly: `_standard_ops()` in `workflow/_pipeliner.py`.
- Public imports: `from conic.workflow import Configurator, Pipeliner`.
- Tools: `tools/<tool>/`, run on processed data, outside the pipeline.
- No processing logic in catalog or pipeliner.

## Catalog Factory

Takes optional step-level overrides (keyword-only, may default), returns
`Operation`. Inside `build(config)`: read config, then
`return bind(pure_fn, **kwargs)`. Derived names are composed here
(`col_qt_rol=output_columns.qt + parameters.rolling_label`).
Conditional ops return a no-op
`Step(name=..., apply=lambda lazy: lazy)` when disabled (e.g.
`max_sleeve_offset == 0`).

## Tools

Autonomous subpackage `tools/<tool>/` owning `_config.py`,
`_columns.py`, `_defaults.py`, `_compute.py`; no `Operation`, no
`Configurator` access. The public fn takes the processed
`pl.DataFrame` plus keyword-only `config: Config | None = None` and
`columns: Columns | None = None` (defaults when `None`), validates its
input columns, and returns a new `DataFrame` collected with
`engine="in-memory"`.

## Pure Function Signatures

`lazy: pl.LazyFrame` first, then positional `col_*: str`, then
keyword-only config values after `*` (Configurator-sourced: no
defaults; toggles like `override`/`digits` may default). Returns
`pl.LazyFrame`.

## Pipeliner

Frozen dataclass. `Pipeliner.standard(config)` builds from
`_standard_ops()`; `Pipeliner.from_operations(config, ops)` for custom
selections; `.run(data) -> DataFrame` lazies input, applies steps,
collects with `engine="in-memory"` (see conic-polars). Input validation implicit via `filter_input_columns` (first
standard step).

## Adding a Standard Op

1. Pure fn in `engine/`. 2. Factory in `workflow/catalog/_clean.py`
or `workflow/catalog/_derive.py`. 3. Insert `Operation` at correct position in
`_standard_ops()`. 4. New defaults: add to `workflow/defaults.toml`, bind
in `workflow/_defaults.py`, add the field to `workflow/_sections.py`.

## Adding a Tool

1. Create `tools/<tool>/` subpackage (files above). 2. Re-export the
public fn, `Config` and `Columns` from its `__init__.py`. 3. Users run
it on the output of `Pipeliner.run`.
