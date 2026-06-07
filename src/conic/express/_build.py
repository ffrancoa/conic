from pathlib import Path
from typing import Any

from conic.engine.config import Configurator, InputColumns, OutputColumns
from conic.engine.pipeline import Operation, Pipeliner

INPUT_COLUMNS = set(InputColumns.model_fields.keys())
OUTPUT_COLUMNS = set(OutputColumns.model_fields.keys())


def _classify_columns(columns: dict[str, str]) -> dict[str, dict[str, str]]:

    unknown_columns = set(columns).difference(INPUT_COLUMNS, OUTPUT_COLUMNS)

    if unknown_columns:
        raise ValueError(f"unknown column keys: {unknown_columns}.")

    input_columns = {}
    output_columns = {}

    for key, name in columns.items():
        if key in INPUT_COLUMNS:
            input_columns[key] = name
        else:
            output_columns[key] = name

    return {"input": input_columns, "output": output_columns}


def build_configurator(
    config_file: Path | str | None = None,
    *,
    parameters: dict[str, float] | None = None,
    cleansing: dict[str, Any] | None = None,
    settings: dict[str, int | float] | None = None,
    columns: dict[str, str] | None = None,
) -> Configurator:

    config = Configurator.from_toml(config_file) if config_file else Configurator()

    overrides: dict[str, Any] = {}

    if parameters is not None:
        overrides["parameters"] = config.parameters.model_dump() | parameters

    if cleansing is not None:
        overrides["cleansing"] = config.cleansing.model_dump() | cleansing

    if settings is not None:
        overrides["settings"] = config.settings.model_dump() | settings

    if columns is not None:
        classified = _classify_columns(columns)
        columns_dump = config.columns.model_dump()
        columns_dump["input"] |= classified["input"]
        columns_dump["output"] |= classified["output"]
        overrides["columns"] = columns_dump

    if not overrides:
        return config

    return Configurator.model_validate(config.model_dump() | overrides)


def build_pipeliner(
    *, config: Configurator | Path | str, steps: tuple[Operation, ...]
) -> Pipeliner:

    if not isinstance(config, Configurator):
        config = Configurator.from_toml(config)

    return Pipeliner.from_operations(config, steps)
