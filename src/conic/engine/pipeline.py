import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from typing import Literal, NamedTuple, Self, TypedDict, cast, overload

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


def _get_dataframe_fingerprint(data: pl.DataFrame) -> str:
    hasher = hashlib.sha256()
    hasher.update(str(data.schema).encode())

    hash_frame = data.hash_rows().to_frame()
    hash_bytes = cast(BytesIO, hash_frame.write_ipc(file=None)).getvalue()

    hasher.update(hash_bytes)

    return hasher.hexdigest()[:16]


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
        return cls.from_operations(config, STANDARD_OPS)

    @classmethod
    def from_operations(
        cls,
        config: Configurator,
        operations: tuple[Operation, ...],
    ) -> Self:
        steps = tuple(operation.build(config) for operation in operations)

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

        lazy = data.lazy()

        for step in self.steps:
            lazy = step.apply(lazy)

        out_data = cast(pl.DataFrame, lazy.collect())

        if not metadata:
            return out_data

        meta: PipelineMetadata = {
            "data_hash": _get_dataframe_fingerprint(data),
            "source_path": None,
            "config": self.config.model_dump(),
            "steps": [step.name for step in self.steps],
            "timestamp_utc": datetime.now(UTC).isoformat(),
        }

        return PipelineResult(data=out_data, metadata=meta)
