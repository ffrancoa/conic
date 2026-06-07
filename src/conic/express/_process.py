import polars as pl

from conic.engine.config import Configurator
from conic.engine.pipeline import Pipeliner, PipelineResult


def process_std(
    data: pl.DataFrame,
    config: Configurator | None = None,
    *,
    metadata: bool = False,
) -> pl.DataFrame | PipelineResult:

    if config is None:
        config = Configurator()

    pipeline = Pipeliner.standard(config)

    return pipeline.run(data, metadata=metadata)
