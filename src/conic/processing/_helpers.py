from collections.abc import Iterable

from polars import DataFrame


def get_missing_columns(data: DataFrame, required_columns: Iterable[str]) -> set:

    return set(required_columns).difference(data.columns)
