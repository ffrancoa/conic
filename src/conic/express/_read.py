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


def read_excel(
    path: Path | str,
    *,
    sheet_number: int | None = None,
    sheet_name: str | None = None,
    skip_rows: int = 0,
) -> pl.DataFrame:

    return pl.read_excel(
        path,
        has_header=True,
        infer_schema_length=None,
        sheet_id=sheet_number,
        sheet_name=sheet_name,
        raise_if_empty=True,
        read_options={"header_row": skip_rows, "skip_rows": skip_rows},
    )
