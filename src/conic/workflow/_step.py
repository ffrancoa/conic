from collections.abc import Callable
from dataclasses import dataclass
from types import FunctionType

import polars as pl

from conic.workflow._configurator import Configurator


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    apply: Callable[[pl.LazyFrame], pl.LazyFrame]


def bind(function: FunctionType, /, **kwargs: object) -> Step:
    def apply(data: pl.LazyFrame) -> pl.LazyFrame:
        return function(data, **kwargs)

    return Step(name=function.__name__, apply=apply)


@dataclass(frozen=True, slots=True)
class Operation:
    build: Callable[[Configurator], Step]
