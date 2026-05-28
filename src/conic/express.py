from pathlib import Path
from typing import Optional

import polars as pl

from .config import Configurator
from .pipeline import Pipeliner, PipelineResult


def process(
    data: pl.DataFrame,
    config: Optional[Configurator, Path, str],
    *,
    parameters: Optional[dict] = None,
    columns: Optional[dict] = None,
    cleansing: Optional[dict] = None,
    metadata: bool = False,
) -> pl.DataFrame | PipelineResult:

    if isinstance(config, Configurator):
        configurator = config
    elif config is not None:
        configurator = Configurator.from_toml(config)
    else:
        configurator_kwargs = {}
        if parameters is not None:
            configurator_kwargs["parameters"] = parameters
        if columns is not None:
            configurator_kwargs["columns"] = columns
        if cleansing is not None:
            configurator_kwargs["cleansing"] = cleansing

        configurator = Configurator.model_validate(configurator_kwargs)

    pipeliner = Pipeliner.default(configurator)

    return pipeliner.run(data, metadata=metadata)
