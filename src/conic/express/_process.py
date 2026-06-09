import polars as pl

from conic.engine.config import Configurator
from conic.engine.pipeline import Pipeliner


def process_std(data: pl.DataFrame, config: Configurator) -> pl.DataFrame:
    return Pipeliner.standard(config).run(data)
