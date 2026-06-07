from pathlib import Path
from typing import Any

import polars as pl

from conic.engine.config import Configurator
from conic.engine.pipeline import Pipeliner, PipelineResult
from conic.express._build import _classify_columns


def process_std(
    data: pl.DataFrame,
    config: Configurator | Path | str | None = None,
    *,
    parameters: dict[str, float] | None = None,
    cleansing: dict[str, Any] | None = None,
    settings: dict[str, int | float] | None = None,
    columns: dict[str, str] | None = None,
    metadata: bool = False,
) -> pl.DataFrame | PipelineResult:

    if config is None:
        config = Configurator()
    elif not isinstance(config, Configurator):
        config = Configurator.from_toml(config)

    config_overrides = {}

    if parameters is not None:
        config_overrides["parameters"] = config.parameters.model_dump() | parameters

    if cleansing is not None:
        config_overrides["cleansing"] = config.cleansing.model_dump() | cleansing

    if settings is not None:
        config_overrides["settings"] = config.settings.model_dump() | settings

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

    if config_overrides:
        config_merged = config.model_dump() | config_overrides
        config = Configurator.model_validate(config_merged)

    pipeline = Pipeliner.standard(config)

    return pipeline.run(data, metadata=metadata)
