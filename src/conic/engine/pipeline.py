from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from types import FunctionType
from typing import Literal, NamedTuple, Self, TypedDict, cast, overload

import polars as pl

from conic.core.calculate import derive, prepare
from conic.engine._utils import get_dataframe_fingerprint
from conic.engine.config import Configurator


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    apply: Callable[[pl.LazyFrame], pl.LazyFrame]


def bind(function: FunctionType, /, **kwargs: object) -> Step:
    def apply(data: pl.LazyFrame) -> pl.LazyFrame:
        return function(data, **kwargs)

    return Step(name=function.__name__, apply=apply)


@dataclass(frozen=True, slots=True)
class StepCatalog:
    config: Configurator

    def sanitize_columns(self) -> Step:
        columns = self.config.columns.input
        return bind(
            prepare.sanitize_columns,
            col_depth=columns.depth,
            col_qc=columns.qc,
            col_fs=columns.fs,
            col_u2=columns.u2,
            col_u0=columns.u0,
            col_sv_eff=columns.sv_eff,
            col_sv_tot=columns.sv_tot,
        )

    def adjust_depth_spacing(self) -> Step:
        columns = self.config.columns.input
        cleansing = self.config.cleansing
        return bind(
            prepare.adjust_depth_spacing,
            start_depth=cleansing.start_depth,
            spacing=cleansing.spacing,
            col_depth=columns.depth,
        )

    def clean_by_indicators(self) -> Step:
        cleansing = self.config.cleansing
        return bind(
            prepare.clean_by_indicators,
            indicators=cleansing.indicators,
            mode=cleansing.clean_mode,
        )

    def compute_hydrostatic_column(self, *, override: bool) -> Step:
        parameters = self.config.parameters
        columns = self.config.columns.input
        return bind(
            prepare.compute_hydrostatic_column,
            water_level=parameters.water_level,
            gamma_water=parameters.gamma_water,
            col_depth=columns.depth,
            col_u0=columns.u0,
            override=override,
        )

    def compute_geostatic_columns(self, *, override: bool) -> Step:
        parameters = self.config.parameters
        columns = self.config.columns.input
        return bind(
            prepare.compute_geostatic_columns,
            gamma_soil=parameters.gamma_soil,
            col_depth=columns.depth,
            col_sv_eff=columns.sv_eff,
            col_sv_tot=columns.sv_tot,
            col_u0=columns.u0,
            override=override,
        )

    def compute_non_normalized_columns(self) -> Step:
        parameters = self.config.parameters
        input_columns = self.config.columns.input
        output_columns = self.config.columns.output
        return bind(
            derive.compute_non_normalized_columns,
            area_ratio=parameters.area_ratio,
            col_sv_tot=input_columns.sv_tot,
            col_u2=input_columns.u2,
            col_fs=input_columns.fs,
            col_qc=input_columns.qc,
            col_qt=output_columns.qt,
            col_qn=output_columns.qn,
            col_rf=output_columns.rf,
        )

    def compute_rolling_columns(self) -> Step:
        parameters = self.config.parameters
        input_columns = self.config.columns.input
        output_columns = self.config.columns.output
        return bind(
            derive.compute_rolling_columns,
            rolling=parameters.rolling,
            col_fs=input_columns.fs,
            col_qt=output_columns.qt,
            col_qn=output_columns.qn,
            rolling_label=parameters.rolling_label,
        )

    def compute_normalized_columns(self) -> Step:
        parameters = self.config.parameters
        input_columns = self.config.columns.input
        output_columns = self.config.columns.output
        return bind(
            derive.compute_normalized_columns,
            col_sv_eff=input_columns.sv_eff,
            col_u0=input_columns.u0,
            col_u2=input_columns.u2,
            col_fs=input_columns.fs,
            col_qn=output_columns.qn,
            col_qt1=output_columns.qt1,
            col_fr=output_columns.fr,
            col_bq=output_columns.bq,
            col_u=output_columns.u,
            rolling_label=parameters.rolling_label,
        )

    def compute_behavior_columns(self) -> Step:
        parameters = self.config.parameters
        settings = self.config.settings
        input_columns = self.config.columns.input
        output_columns = self.config.columns.output
        return bind(
            derive.compute_behavior_columns,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
            col_qt=output_columns.qt,
            col_fr=output_columns.fr,
            col_n=output_columns.n,
            col_qtn=output_columns.qtn,
            col_ic=output_columns.ic,
            col_convg=output_columns.convg,
            col_cd=output_columns.cd,
            col_ib=output_columns.ib,
            p_ref=settings.p_ref,
            max_iter=settings.max_iter,
            tolerance=settings.tolerance,
            rolling_label=parameters.rolling_label,
        )


@dataclass(frozen=True, slots=True)
class Operation:
    build: Callable[[StepCatalog], Step]


class PipelineMetadata(TypedDict):
    data_hash: str
    source_path: str | None
    config: dict[str, object]
    steps: list[str]
    timestamp_utc: str


class PipelineResult(NamedTuple):
    data: pl.DataFrame
    metadata: PipelineMetadata


@dataclass(frozen=True, slots=True)
class Pipeliner:
    config: Configurator
    steps: tuple[Step, ...]

    @classmethod
    def standard(cls, config: Configurator) -> Self:
        catalog = StepCatalog(config)

        steps = (
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

        return cls(config=config, steps=steps)

    @classmethod
    def from_operations(
        cls,
        config: Configurator,
        operations: tuple[Operation, ...],
    ) -> Self:
        catalog = StepCatalog(config)
        steps = tuple(operation.build(catalog) for operation in operations)

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

        lazy_data = data.lazy()

        for step in self.steps:
            lazy_data = step.apply(lazy_data)

        out_data = cast(pl.DataFrame, lazy_data.collect())

        if not metadata:
            return out_data

        meta: PipelineMetadata = {
            "data_hash": get_dataframe_fingerprint(data),
            "source_path": None,
            "config": self.config.model_dump(),
            "steps": [step.name for step in self.steps],
            "timestamp_utc": datetime.now(UTC).isoformat(),
        }

        return PipelineResult(data=out_data, metadata=meta)
