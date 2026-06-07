from typing import Literal

import polars as pl
from polars.exceptions import ColumnNotFoundError

from conic.core._utils import get_missing_columns

COL_QC1_OS02: str = "qc1 (MPa) [OS02]"
COL_SU_LIQ_RATIO_OS02: str = "Su_liq (-) [OS02]"

MAX_SU_LIQ_RATIO: float = 0.15
SU_LIQ_RATIO_STD: float = 0.03


def compute_qc1(
    lazy: pl.LazyFrame,
    *,
    p_ref: float,
    rolling: int,
    col_sv_eff: str,
    col_qc: str,
    col_qc1: str = COL_QC1_OS02,
) -> pl.LazyFrame:

    if missing_columns := get_missing_columns(lazy, {col_sv_eff, col_qc}):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    col_qc_rol = (
        pl.col(col_qc)
        .rolling_mean(window_size=rolling, min_samples=rolling, center=True)
        .fill_null(float("nan"))
    )

    return lazy.with_columns(
        ((col_qc_rol * 1.8) / (0.8 + (pl.col(col_sv_eff) / p_ref))).alias(col_qc1)
    )


def compute_su_liq_ratio(
    lazy: pl.LazyFrame,
    *,
    bound: Literal["mean", "lower", "upper"],
    col_qc1: str = COL_QC1_OS02,
    col_su_liq_ratio: str = COL_SU_LIQ_RATIO_OS02,
    max_su_liq_ratio: float = MAX_SU_LIQ_RATIO,
) -> pl.LazyFrame:

    match bound:
        case "mean":
            epsilon = 0.00
        case "lower":
            epsilon = -SU_LIQ_RATIO_STD
        case "upper":
            epsilon = SU_LIQ_RATIO_STD

    return lazy.with_columns(
        (
            pl.when(pl.col(col_qc1) <= 6.5)
            .then(0.03 + 0.0143 * pl.col(col_qc1) + epsilon)
            .otherwise(float("nan"))
            .clip(upper_bound=max_su_liq_ratio)
        ).alias(col_su_liq_ratio)
    )
