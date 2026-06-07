from polars import LazyFrame


def get_column_names(lazy: LazyFrame) -> list[str]:
    return lazy.collect_schema().names()


def get_missing_columns(
    lazy: LazyFrame, required_columns: list[str] | set[str]
) -> set[str]:

    columns = get_column_names(lazy)
    missing_columns = set(required_columns).difference(columns)

    return missing_columns
