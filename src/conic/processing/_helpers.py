from collections.abc import Iterable

import polars as pl


def get_missing_columns(data: pl.DataFrame, required_columns: Iterable[str]) -> set:

    return set(required_columns).difference(data.columns)
