from collections.abc import Iterable

import polars as pl


def get_column_names(data: pl.DataFrame | pl.LazyFrame) -> list[str]:
    if isinstance(data, pl.LazyFrame):
        return data.collect_schema().names()
    return data.columns


def get_missing_columns(
    data: pl.DataFrame | pl.LazyFrame, required_columns: Iterable[str]
) -> set:
    return set(required_columns).difference(get_column_names(data))
