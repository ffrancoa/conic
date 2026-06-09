import dataclasses
from pathlib import Path
from typing import Any

from conic.engine.config import Configurator, InputColumns, OutputColumns
from conic.engine.pipeline import Operation, Pipeliner

INPUT_COLUMNS = {field.name for field in dataclasses.fields(InputColumns)}
OUTPUT_COLUMNS = {field.name for field in dataclasses.fields(OutputColumns)}
dataclasses.field()


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
        overrides["parameters"] = dataclasses.asdict(config.parameters) | parameters

    if cleansing is not None:
        overrides["cleansing"] = dataclasses.asdict(config.cleansing) | cleansing

    if settings is not None:
        overrides["settings"] = dataclasses.asdict(config.settings) | settings

    if columns is not None:
        classified = _classify_columns(columns)
        columns_dump = dataclasses.asdict(config.columns)
        columns_dump["input"] |= classified["input"]
        columns_dump["output"] |= classified["output"]
        overrides["columns"] = columns_dump

    if not overrides:
        return config

    return Configurator.from_dict(dataclasses.asdict(config) | overrides)


def build_pipeliner(
    *, config: Configurator | Path | str, steps: tuple[Operation, ...]
) -> Pipeliner:

    if not isinstance(config, Configurator):
        config = Configurator.from_toml(config)

    return Pipeliner.from_operations(config, steps)
