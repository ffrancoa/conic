import hashlib

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from typing import Literal, NamedTuple, Self, cast, overload

import polars as pl

from conic.config import Configurator
from conic.processing import derivation, preparation


def _dataframe_fingerprint(data: pl.DataFrame):
    data_to_bytes = cast(BytesIO, data.write_ipc(file=None)).getvalue()

    hash_text = hashlib.sha256(data_to_bytes).hexdigest()

    return hash_text[:16]


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    apply: Callable[[pl.DataFrame], pl.DataFrame]


@dataclass(frozen=True, slots=True)
class StepCatalog:
    config: Configurator

    def sanitize_data(self) -> Step:
        function = preparation.sanitize_data
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

    def adjust_depth_spacing(self) -> Step:
        function = preparation.adjust_depth_spacing
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

    def clean_by_indicators(self) -> Step:
        function = preparation.clean_by_indicators
        cleansing = self.config.cleansing

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data, indicators=cleansing.indicators, mode=cleansing.clean_mode
            )

        return Step(name=function.__name__, apply=callback)

    def compute_hydrostatic(self) -> Step:
        function = preparation.compute_hydrostatic
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

    def compute_geostatic(self) -> Step:
        function = preparation.compute_geostatic
        parameters = self.config.parameters
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                gamma_soil=parameters.gamma_soil,
                col_depth=columns.input.depth,
                col_sv_eff=columns.input.sv_eff,
                col_sv_tot=columns.input.sv_tot,
                col_u0=columns.input.u0,
                override=True,
            )

        return Step(name=function.__name__, apply=callback)

    def compute_non_normalized(self) -> Step:
        function = derivation.compute_non_normalized
        parameters = self.config.parameters
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                area_ratio=parameters.area_ratio,
                col_fs=columns.input.fs,
                col_qc=columns.input.qc,
                col_qt=columns.output.qt,
                col_rf=columns.output.rf,
                col_u2=columns.input.u2,
            )

        return Step(name=function.__name__, apply=callback)

    def compute_rolling_columns(self) -> Step:
        function = derivation.compute_rolling_columns
        parameters = self.config.parameters
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                rolling=parameters.rolling,
                col_fs=columns.input.fs,
                col_qt=columns.output.qt,
            )

        return Step(name=function.__name__, apply=callback)

    def compute_normalized(self) -> Step:
        function = derivation.compute_normalized
        columns = self.config.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                col_sv_eff=columns.input.sv_eff,
                col_sv_tot=columns.input.sv_tot,
                col_fs=columns.input.fs,
                col_qt=columns.output.qt,
                col_u0=columns.input.u0,
                col_u2=columns.input.u2,
                col_qt1=columns.output.qt1,
                col_fr=columns.output.fr,
                col_bq=columns.output.bq,
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
    def standard(cls, config: Configurator) -> Self:
        catalog = StepCatalog(config)

        steps = (
            catalog.sanitize_data(),
            catalog.adjust_depth_spacing(),
            catalog.clean_by_indicators(),
            catalog.compute_hydrostatic(),
            catalog.compute_geostatic(),
            catalog.compute_non_normalized(),
            catalog.compute_rolling_columns(),
            catalog.compute_normalized(),
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
            "data_hash": _dataframe_fingerprint(data),
            "source_path": None,
            "config": self.config.model_dump(),
            "steps": [step.name for step in self.steps],
            "timestamp_utc": datetime.now(UTC).isoformat,
        }

        return PipelineResult(data=out_data, metadata=meta)
