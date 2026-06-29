---
name: conic-step
description: >
  Step and Operation architecture in conic. Use when creating,
  modifying, or reviewing pipeline operations, catalog factories,
  or the bind mechanism that connects pure functions to configuration.
---

## Core Abstractions

Three types, all frozen dataclasses in `engine/step.py`:

- **Step**: a `name` paired with an `apply` callable
  (`LazyFrame -> LazyFrame`), already closed over its parameters.
  Ready to execute.

- **Operation**: wraps a deferred builder
  `build: Callable[[Configurator], Step]`. A step not yet bound
  to a configuration. Materialized into a `Step` when a pipeline
  is constructed.

- **bind(function, **kwargs)**: closes a pure function over its
  config-derived keyword arguments and derives the step `name`
  from `function.__name__`. Returns a `Step`.

The lifecycle: `Operation.build(config)` calls `bind(function, **kwargs)`
where kwargs are extracted from the `Configurator`.

## Where Each Piece Lives

- Pure functions: `core/calculate/` or `core/correlations/`. Self-sufficient,
  no dependency on engine types.
- Catalog factories: `engine/catalog.py`. Each factory is a public
  function `(**step_params) -> Operation` whose inner `build(config)`
  maps the `Configurator` to the pure function's kwargs via `bind`.
- Pipeline assembly: `engine/pipeline.py`. `STANDARD_OPS` is the
  ordered tuple of `Operation` instances backing the full CPTu flow.

No processing logic in `catalog.py` or `pipeline.py`. These layers
only wire configuration to pure functions.

## Writing a Catalog Factory

A factory receives optional step-level parameters (overrides the user
can pass when composing a custom pipeline) and returns an `Operation`.
Inside the `Operation`, the `build` closure reads from `config` and
calls `bind`:

- Extract needed values from the appropriate sub-model
  (`config.parameters`, `config.cleansing`, `config.settings`,
  `config.columns`).
- Pass them as keyword arguments matching the pure function's
  signature (native types only).
- Return `bind(pure_function, **kwargs)`.

If the operation is conditional (e.g., `align_sounding` is opt-in),
the factory checks the config flag and returns a no-op `Step` or
skips binding accordingly.

## Pure Function Signatures

- Accept `lazy: pl.LazyFrame` as first positional argument.
- Column names as positional `col_*: str` parameters (after `lazy`),
  with defaults from module-level constants where applicable.
- Remaining configuration-derived values as keyword-only arguments
  (after `*`) with defaults from `_canonical.py` where applicable.
- Return `pl.LazyFrame`.
- No imports from `engine/`. No `Configurator`, `Step`, or
  `Operation` in the signature or body.

## Adding an Operation to the Standard Pipeline

1. Write the pure function in the appropriate `core/` module.
2. Write the catalog factory in `catalog.py`.
3. Insert the `Operation` in `STANDARD_OPS` at the correct
   position — order matters, each step may depend on columns
   produced by earlier steps.
4. If the operation needs a config flag or parameter, add the
   default to `_canonical.py` and the field to the corresponding
   sub-model in `config.py` (with `__post_init__` validation
   if needed).

## Pipeliner

`Pipeliner` is `@dataclass(frozen=True, slots=True)`.

- `Pipeliner.standard(config)`: builds from `STANDARD_OPS`.
- `Pipeliner.from_operations(config, operations)`: arbitrary
  pipeline from a tuple of `Operation`.
- `Pipeliner(config=..., steps=...)` direct construction is public API.
- `run(data) -> pl.DataFrame`: converts input to lazy, applies
  steps in order, collects.
- Input validation is implicit — `sanitize_sounding` (the first
  standard step) raises `ColumnNotFoundError` if required columns
  are missing.
