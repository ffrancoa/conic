from pathlib import Path

import polars as pl


def read_csv(
    path: Path | str, *, delimiter: str = ",", skip_records: int = 0
) -> pl.DataFrame:

    return pl.read_csv(
        path,
        has_header=True,
        infer_schema=False,
        raise_if_empty=True,
        separator=delimiter,
        skip_rows_after_header=skip_records,
    ).cast({pl.String: pl.Float64})
