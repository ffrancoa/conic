from collections.abc import Iterable

import polars as pl


def scale_column(column_name: str, scale_factor: float) -> pl.Expr:
    return pl.col(column_name) * scale_factor


def get_column_names(data: pl.LazyFrame) -> list[str]:
    return data.collect_schema().names()


def get_missing_columns(data: pl.LazyFrame, required_columns: Iterable[str]) -> set:
    return set(required_columns).difference(get_column_names(data))
