---
name: conic-docs
description: >
  Docstring conventions for conic. Use when writing, modifying,
  or reviewing docstrings in any module.
---

## Format

NumPy style. Max line length 72 characters (PEP 257). No blank
line between the closing `"""` and the first line of code.

## Structure

1. **Summary line**: one sentence, imperative mood. Describes
   what the function does from the perspective of a geotechnical
   engineer using the library, not implementation details.
2. **Extended description** (optional): only when the summary
   cannot stand alone. Explain *why* the function behaves a
   certain way (e.g. why columns are cast, why a parameter
   exists). No redundancy with the summary.
3. **Parameters**: one entry per parameter. Include type and
   default after the name (`param : type, default value`).
   Use prose types (`str or None`, `Path or str`), not Python
   syntax (`str | None`). Description focuses on what the
   user needs to know, not internal handling.
4. **Returns**: type on its own line, description indented below.
5. **Raises** (optional): only document exceptions the caller
   should anticipate. Fully qualified exception name.
6. **Examples** (optional): realistic CPTu usage. Use `>>>`
   continuation (`...`) to stay within 72 chars. Show output
   only when it clarifies the result.

## Audience

Write for a geotechnical engineer who understands CPTu data but
may not be a Python expert. Use domain terms naturally (`qc`,
`fs`, `u2`, `header row`, `units row`) without over-explaining
them. Explain Polars or Python behavior only when non-obvious
(e.g. strict cast, schema inference depth).

## What to Document

- All public functions (no leading underscore).
- Public classes and their `__init__` (via class-level docstring).

Do not document:
- Private functions (`_expr_*`, `_compute_*`, `_validate_*`).
- Module-level constants.
- Re-exports in `__init__.py`.

## Avoid

- Repeating the type hint as the entire parameter description.
- Implementation details that belong in code comments.
- References to internal modules, config fields, or pipeline
  stages that the end user does not interact with.
- Trailing blank lines inside the docstring.
