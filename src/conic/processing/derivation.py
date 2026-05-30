import polars as pl

from polars.exceptions import ColumnNotFoundError

from conic._canonical import (
    COL_QC,
    COL_QT,
    COL_U2,
)
from conic.processing._helpers import get_missing_columns


def compute_qt(
    data: pl.DataFrame,
    area_ratio: float,
    *,
    col_qc: str = COL_QC,
    col_qt: str = COL_QT,
    col_u2: str = COL_U2,
) -> pl.DataFrame:

    if missing_columns := get_missing_columns(data, {col_qc, col_u2}):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    return data.with_columns(
        (pl.col(col_qc) + (1 - area_ratio) * (pl.col(col_u2) / 1000.0)).alias(col_qt)
    )
