from pathlib import Path
from typing import Optional

import polars as pl

from .config import Configurator, InputColumns, OutputColumns
from .pipeline import Pipeliner, PipelineResult

_INPUT_COLS = set(InputColumns.model_fields.keys())
_OUTPUT_COLS = set(OutputColumns.model_fields.keys())


def read_csv(
    path: Path | str, *, delimiter: str = ",", skip_rows: int = 0
) -> pl.DataFrame:

    return pl.read_csv(
        path,
        has_header=True,
        separator=delimiter,
        schema_overrides=[pl.Float64],
        skip_rows_after_header=skip_rows,
        raise_if_empty=True,
    )


def process(
    data: pl.DataFrame,
    config: Optional[Configurator | Path | str],
    *,
    parameters: Optional[dict] = None,
    columns: Optional[dict] = None,
    cleansing: Optional[dict] = None,
    metadata: bool = False,
) -> pl.DataFrame | PipelineResult:

    if isinstance(config, Configurator):
        config = config
    elif config is not None:
        config = Configurator.from_toml(config)
    else:
        config = Configurator()

    config_overrides = {}

    if parameters is not None:
        config_overrides["parameters"] = config.parameters.model_dump() | parameters

    if columns is not None:
        unknown_columns = set(columns).difference(_INPUT_COLS, _OUTPUT_COLS)
        if unknown_columns:
            raise ValueError(f"Unknown column keys: {unknown_columns}.")

        columns_dump = config.columns.model_dump()

        input_cols_overrides = {}
        output_cols_overrides = {}

        for key, new_name in columns.items():
            if key in _INPUT_COLS:
                input_cols_overrides[key] = new_name
            else:
                output_cols_overrides[key] = new_name

        if input_cols_overrides:
            columns_dump["input"] = columns_dump["input"] | input_cols_overrides
        if output_cols_overrides:
            columns_dump["output"] = columns_dump["output"] | output_cols_overrides

        config_overrides["columns"] = columns_dump

    if cleansing is not None:
        config_overrides["cleansing"] = config.cleansing.model_dump() | cleansing

    if config_overrides:
        config_merged = config.model_dump() | config_overrides
        config = Configurator.model_validate(config_merged)

    pipeline = Pipeliner.default(config)

    return pipeline.run(data, metadata=metadata)
