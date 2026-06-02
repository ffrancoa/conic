from pathlib import Path
from typing import Any, Literal, Optional

import polars as pl

from .config import (
    Configurator as _Configurator,
    InputColumns as _InputColumns,
    OutputColumns as _OutputColumns,
)
from .pipeline import (
    Pipeliner as _Pipeliner,
    PipelineResult as _PipelineResult,
)

_INPUT_COLS = set(_InputColumns.model_fields.keys())
_OUTPUT_COLS = set(_OutputColumns.model_fields.keys())


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


def read_csv(
    path: Path | str, *, delimiter: str = ",", skip_records: int = 0
) -> pl.DataFrame:

    return pl.read_csv(
        path,
        has_header=True,
        infer_schema_length=False,
        raise_if_empty=True,
        separator=delimiter,
        skip_rows_after_header=skip_records,
    ).select(pl.all().cast(pl.Float64, strict=False))


def build_configurator(
    *,
    columns: Optional[dict[str, str]] = None,
    parameters: Optional[dict[str, float]] = None,
    cleansing: Optional[dict[str, Any]] = None,
) -> _Configurator:

    return _Configurator.model_validate(
        {
            "columns": _classify_columns(columns) if columns else {},
            "parameters": parameters or {},
            "cleansing": cleansing or {},
        }
    )


def process_std(
    data: pl.DataFrame,
    config: Optional[_Configurator | Path | str] = None,
    std_pipeliner: Literal["A0", "A1", "B0", "B1"] = "B1",
    *,
    parameters: Optional[dict[str, float]] = None,
    columns: Optional[dict[str, str]] = None,
    cleansing: Optional[dict[str, Any]] = None,
    metadata: bool = False,
) -> pl.DataFrame | _PipelineResult:

    if config is None:
        config = _Configurator()
    elif not isinstance(config, _Configurator):
        config = _Configurator.from_toml(config)

    config_overrides = {}

    if parameters is not None:
        config_overrides["parameters"] = config.parameters.model_dump() | parameters

    if columns is not None:
        columns_dump = config.columns.model_dump()
        columns_overrides = _classify_columns(columns)

        if columns_overrides["input"]:
            columns_dump["input"] = columns_dump["input"] | columns_overrides["input"]

        if columns_overrides["output"]:
            columns_dump["output"] = (
                columns_dump["output"] | columns_overrides["output"]
            )

        config_overrides["columns"] = columns_dump

    if cleansing is not None:
        config_overrides["cleansing"] = config.cleansing.model_dump() | cleansing

    if config_overrides:
        config_merged = config.model_dump() | config_overrides
        config = _Configurator.model_validate(config_merged)

    match std_pipeliner:
        case "A0":
            pipeline = _Pipeliner.standard_a0(config)
        case "A1":
            pipeline = _Pipeliner.standard_a1(config)
        case "B0":
            pipeline = _Pipeliner.standard_b0(config)
        case "B1":
            pipeline = _Pipeliner.standard_b1(config)

    return pipeline.run(data, metadata=metadata)
