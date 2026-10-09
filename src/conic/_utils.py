from polars import LazyFrame
from polars.exceptions import ColumnNotFoundError


def check_required_columns(lazy: LazyFrame, required_columns: set[str]) -> None:
    columns = lazy.collect_schema().names()

    if missing_columns := required_columns.difference(columns):
        raise ColumnNotFoundError(f"missing required columns: {missing_columns}")


def has_column(lazy: LazyFrame, column: str) -> bool:
    return column in lazy.collect_schema().names()
