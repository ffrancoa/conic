from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, NamedTuple, Self, overload

import polars as pl

from .config import Processor
from .validation import get_fingerprint, validate_columns
from . import preprocess


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    apply: Callable[[pl.DataFrame], pl.DataFrame]

@dataclass(frozen=True, slots=True)
class StepCatalog:
    processor: Processor

    def compute_hydrostatic(self) -> Step:
        function = preprocess.compute_hydrostatic
        parameters = self.processor.parameters
        columns = self.processor.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                water_level=parameters.water_level,
                gamma_water=parameters.gamma_water,
                col_depth=columns.input.depth,
                col_u0=columns.input.u0,
                override=True
            )

        return Step(name=function.__name__, apply=callback)

    def adjust_depth_spacing(self) -> Step:
        function = preprocess.adjust_depth_spacing
        cleansing = self.processor.cleansing
        columns = self.processor.columns

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                start_depth=cleansing.start_depth,
                spacing=cleansing.spacing,
                col_depth=columns.input.depth
            )

        return Step(name=function.__name__, apply=callback)

    def clean_by_indicators(self) -> Step:
        function = preprocess.clean_by_indicators
        cleansing = self.processor.cleansing

        def callback(data: pl.DataFrame) -> pl.DataFrame:
            return function(
                data,
                indicators=cleansing.indicators,
                mode=cleansing.clean_mode
            )

        return Step(name=function.__name__, apply=callback)

class PipelineResult(NamedTuple):
    data: pl.DataFrame
    metadata: dict[str, object]

@dataclass(frozen=True, slots=True)
class Pipeliner:
    processor: Processor
    steps: tuple[Step, ...]

    @classmethod
    def default(cls, processor: Processor) -> Self:
        catalog = StepCatalog(processor)
        
        steps = (
            catalog.adjust_depth_spacing(),
            catalog.clean_by_indicators(),
            catalog.compute_hydrostatic()
        )

        return cls(processor=processor, steps=steps)

    @overload
    def run(
            self,
            inp_data: pl.DataFrame, *,
            metadata: Literal[False] = False,
            validate: bool = True
        ) -> pl.DataFrame: ...
    @overload
    def run(
            self,
            inp_data: pl.DataFrame, *,
            metadata: Literal[True],
            validate: bool = True
        ) -> PipelineResult: ...
    def run(
            self,
            inp_data: pl.DataFrame, *,
            metadata: bool = False,
            validate: bool = True
        ) -> pl.DataFrame | PipelineResult:

        if validate:
            validate_columns(inp_data, self.processor)

        out_data = inp_data

        for step in self.steps:
            out_data = step.apply(out_data)
            
        if not metadata:
            return out_data

        meta = {
            "data_hash": get_fingerprint(inp_data),
            "source_path": None,
            "processor": self.processor.model_dump(),
            "steps": [step.name for step in self.steps],
            "timestamp_utc": datetime.now(timezone.utc).isoformat
        }

        return PipelineResult(data=out_data, metadata=meta)

