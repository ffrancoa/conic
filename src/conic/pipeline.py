from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, NamedTuple, Self, overload

import polars as pl

from conic import preprocess
from conic._helpers import dataframe_fingerprint
from conic.config import Configurator


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    apply: Callable[[pl.DataFrame], pl.DataFrame]


@dataclass(frozen=True, slots=True)
class StepCatalog:
    config: Configurator

    def adjust_depth_spacing(self) -> Step:
        function = preprocess.adjust_depth_spacing
        cleansing = self.config.cleansing
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                start_depth=cleansing.start_depth,
                spacing=cleansing.spacing,
                col_depth=columns.input.depth,
            )

        return Step(name=function.__name__, apply=callback)

    def sanitize_data(self) -> Step:
        function = preprocess.sanitize_data
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                col_depth=columns.input.depth,
                col_qc=columns.input.qc,
                col_fs=columns.input.fs,
                col_u2=columns.input.u2,
                col_u0=columns.input.u0,
                col_sv_eff=columns.input.sv_eff,
                col_sv_tot=columns.input.sv_tot,
            )

        return Step(name=function.__name__, apply=callback)

    def compute_hydrostatic(self) -> Step:
        function = preprocess.compute_hydrostatic
        parameters = self.config.parameters
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                water_level=parameters.water_level,
                gamma_water=parameters.gamma_water,
                col_depth=columns.input.depth,
                col_u0=columns.input.u0,
                override=True,
            )

        return Step(name=function.__name__, apply=callback)

    def clean_by_indicators(self) -> Step:
        function = preprocess.clean_by_indicators
        cleansing = self.config.cleansing

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data, indicators=cleansing.indicators, mode=cleansing.clean_mode
            )

        return Step(name=function.__name__, apply=callback)


class PipelineResult(NamedTuple):
    data: pl.DataFrame
    metadata: dict[str, object]


@dataclass(frozen=True, slots=True)
class Pipeliner:
    config: Configurator
    steps: tuple[Step, ...]

    @classmethod
    def default(cls, config: Configurator) -> Self:
        catalog = StepCatalog(config)

        steps = (
            catalog.sanitize_data(),
            catalog.adjust_depth_spacing(),
            catalog.clean_by_indicators(),
            catalog.compute_hydrostatic(),
        )

        return cls(config=config, steps=steps)

    @overload
    def run(
        self,
        data: pl.DataFrame,
        *,
        metadata: Literal[False] = False,
    ) -> pl.DataFrame: ...

    @overload
    def run(
        self,
        data: pl.DataFrame,
        *,
        metadata: Literal[True],
    ) -> PipelineResult: ...

    def run(
        self, data: pl.DataFrame, *, metadata: bool = False
    ) -> pl.DataFrame | PipelineResult:

        out_data = data

        for step in self.steps:
            out_data = step.apply(out_data)

        if not metadata:
            return out_data

        meta = {
            "data_hash": dataframe_fingerprint(data),
            "source_path": None,
            "config": self.config.model_dump(),
            "steps": [step.name for step in self.steps],
            "timestamp_utc": datetime.now(UTC).isoformat,
        }

        return PipelineResult(data=out_data, metadata=meta)
