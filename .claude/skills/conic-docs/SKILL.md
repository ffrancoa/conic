---
name: conic-docs
description: >
  Docstring and changelog conventions for conic. Use when writing,
  modifying, or reviewing docstrings or CHANGELOG.md entries.
---

## Docstrings

NumPy style, max line 72 chars (PEP 257). No blank line between closing
`"""` and the first line of code; no trailing blank lines inside.

Coverage is deliberately narrow: the user-facing surface only —
`express` functions and the `Configurator`/`Pipeliner` classes and
public methods. Do NOT add docstrings to catalog factories, pure
processing/correlation functions, `datasets`, `tools`, plugin
wrappers, private fns (`_expr_*`, `_compute_*`, `_validate_*`), module
constants, or `__init__.py` re-exports.

Structure (later sections optional):
1. **Summary**: one imperative sentence from the geotech user's view,
   not implementation.
2. **Extended description**: only if summary can't stand alone; explain
   *why* (a cast, a param's existence). No redundancy.
3. **Parameters**: `param : type, default value` per entry; prose types
   (`str or None`, `Path or str`), not `str | None`. Describe what the
   user needs, not internal handling.
4. **Returns**: type on its own line, description indented below.
5. **Raises**: only exceptions the caller anticipates; fully qualified.
6. **Examples**: realistic CPTu usage; `>>>` with `...` continuation
   under 72 chars; show output only when it clarifies.

Audience: a geotech engineer fluent in CPTu (`qc`, `fs`, `u2`, `header
row`) but not necessarily Python. Explain Polars/Python behavior only
when non-obvious (strict cast, schema inference depth).

Avoid: restating the type hint as the whole param description;
implementation details (belong in comments); references to internal
modules/config fields/pipeline stages the user never touches.

## Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) +
[SemVer](https://semver.org/spec/v2.0.0.html).

- `[Unreleased]` always at top, even if empty. Version heading
  `## [x.y.z] — YYYY-MM-DD` (em-dash). Comparison links at file bottom.
- Section order `Added`, `Changed`, `Removed`; omit empty ones.
- Factual third-person prose; no second-person ("you can now..."), no
  marketing ("finally!"). One cohesive change per bullet; chain related
  details with semicolons, not extra bullets. No trailing period.
- API in backticks: modules dotted (`conic.datasets`), functions with
  parens (`load_dataset()`), classes bare (`Configurator`), params with
  no parens (`metadata=`). External versions as links:
  `` [`1.42.0`](https://github.com/...) ``.
- Audience as docstrings: describe user-visible change, not internal
  refactors unless they show (import path, dependency, performance).
