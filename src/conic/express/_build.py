from pathlib import Path
from typing import Any

from conic.engine.config import Configurator, InputColumns, OutputColumns
from conic.engine.pipeline import Operation, Pipeliner

_INPUT_COLS = set(InputColumns.model_fields.keys())
_OUTPUT_COLS = set(OutputColumns.model_fields.keys())


def _classify_columns(columns: dict[str, str]) -> dict[str, dict[str, str]]:

    unknown_columns = set(columns).difference(_INPUT_COLS, _OUTPUT_COLS)

    if unknown_columns:
        raise ValueError(f"unknown column keys: {unknown_columns}.")

    input_columns = {}
    output_columns = {}

    for key, name in columns.items():
        if key in _INPUT_COLS:
            input_columns[key] = name
        else:
            output_columns[key] = name

    return {"input": input_columns, "output": output_columns}


def build_configurator(
    *,
    parameters: dict[str, float] | None = None,
    cleansing: dict[str, Any] | None = None,
    settings: dict[str, int | float] | None = None,
    columns: dict[str, str] | None = None,
) -> Configurator:

    return Configurator.model_validate(
        {
            "parameters": parameters or {},
            "cleansing": cleansing or {},
            "settings": settings or {},
            "columns": _classify_columns(columns) if columns else {},
        }
    )


def build_pipeliner(
    *, config: Configurator | Path | str, steps: tuple[Operation, ...]
) -> Pipeliner:

    if not isinstance(config, Configurator):
        config = Configurator.from_toml(config)

    return Pipeliner.from_operations(config, steps)
