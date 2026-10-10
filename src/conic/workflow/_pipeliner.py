from dataclasses import dataclass
from typing import Self

import polars as pl

from conic.workflow._configurator import Configurator
from conic.workflow._step import Operation, Step


def _standard_ops() -> tuple[Operation, ...]:
    from conic.workflow import catalog

    return (
        catalog.filter_input_columns(),
        catalog.adjust_depth_spacing(),
        catalog.align_sleeve_column(),
        catalog.clean_by_indicators(),
        catalog.floor_input_columns(),
        catalog.compute_hydrostatic_column(override=True),
        catalog.compute_geostatic_columns(override=True),
        catalog.compute_non_normalized_columns(),
        catalog.compute_rolling_columns(),
        catalog.compute_normalized_columns(),
        catalog.compute_behavior_columns(),
    )


@dataclass(frozen=True, slots=True)
class Pipeliner:
    """Apply a sequence of processing steps to CPTu data.

    Build a pipeliner with ``standard`` for the full default
    sequence, or with ``from_operations`` to select and order
    specific catalog operations.

    Parameters
    ----------
    config : Configurator
        Processing configuration bound into each step.
    steps : tuple of Step
        Ordered processing steps to apply.

    Examples
    --------
    >>> pipe = Pipeliner.standard(config)
    >>> result = pipe.run(raw_data)

    >>> ops = (catalog.filter_input_columns(),
    ...        catalog.compute_non_normalized_columns())
    >>> pipe = Pipeliner.from_operations(config, ops)
    """

    config: Configurator
    steps: tuple[Step, ...]

    @classmethod
    def standard(cls, config: Configurator) -> Self:
        """Create a pipeliner with the full standard sequence.

        Parameters
        ----------
        config : Configurator
            Processing configuration.

        Returns
        -------
        Pipeliner
        """
        return cls.from_operations(config, _standard_ops())

    @classmethod
    def from_operations(
        cls,
        config: Configurator,
        operations: tuple[Operation, ...],
    ) -> Self:
        """Create a pipeliner from a custom set of operations.

        Parameters
        ----------
        config : Configurator
            Processing configuration.
        operations : tuple of Operation
            Ordered catalog operations to include.

        Returns
        -------
        Pipeliner
        """
        steps = tuple(operation.build(config) for operation in operations)

        return cls(config=config, steps=steps)

    def run(self, data: pl.DataFrame) -> pl.DataFrame:
        """Run all steps on a sounding and collect the result.

        Parameters
        ----------
        data : pl.DataFrame
            Raw CPTu sounding data.

        Returns
        -------
        pl.DataFrame
            Processed sounding with all derived columns
            appended.
        """
        lazy = data.lazy()

        for step in self.steps:
            lazy = step.apply(lazy)

        return lazy.collect(engine="in-memory")
