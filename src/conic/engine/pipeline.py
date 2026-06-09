from dataclasses import dataclass
from typing import Self, cast

import polars as pl

from conic.engine import catalog
from conic.engine.config import Configurator
from conic.engine.step import Operation, Step

STANDARD_OPS: tuple[Operation, ...] = (
    catalog.sanitize_columns(),
    catalog.adjust_depth_spacing(),
    catalog.clean_by_indicators(),
    catalog.compute_hydrostatic_column(override=True),
    catalog.compute_geostatic_columns(override=True),
    catalog.compute_non_normalized_columns(),
    catalog.compute_rolling_columns(),
    catalog.compute_normalized_columns(),
    catalog.compute_behavior_columns(),
)


@dataclass(frozen=True, slots=True)
class Pipeliner:
    config: Configurator
    steps: tuple[Step, ...]

    @classmethod
    def standard(cls, config: Configurator) -> Self:
        return cls.from_operations(config, STANDARD_OPS)

    @classmethod
    def from_operations(
        cls,
        config: Configurator,
        operations: tuple[Operation, ...],
    ) -> Self:
        steps = tuple(operation.build(config) for operation in operations)

        return cls(config=config, steps=steps)

    def run(self, data: pl.DataFrame, *, metadata: bool = False) -> pl.DataFrame:

        lazy = data.lazy()

        for step in self.steps:
            lazy = step.apply(lazy)

        return cast(pl.DataFrame, lazy.collect())
