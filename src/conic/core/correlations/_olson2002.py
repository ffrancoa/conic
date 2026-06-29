import polars as pl
from polars.exceptions import ColumnNotFoundError

from conic.core._utils import get_missing_columns

COL_QC1_OS02: str = "qc1 (MPa) [OS02]"
COL_SU_LIQ_RATIO_OS02: str = "Su_liq (-) [OS02]"

MAX_SU_LIQ_RATIO: float = 0.15
SU_LIQ_RATIO_STD: float = 0.03


def compute_qc1(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_qt: str,
    col_qc1: str = COL_QC1_OS02,
    *,
    rolling_label: str,
    p_ref: float,
) -> pl.LazyFrame:

    col_qt_rol = col_qt + rolling_label

    if missing_columns := get_missing_columns(lazy, {col_sv_eff, col_qt_rol}):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    return lazy.with_columns(
        (
            (1.8 * pl.col(col_qt_rol)) / (0.8 + (pl.col(col_sv_eff) / p_ref))
        ).alias(col_qc1)
    )  # fmt: off


def compute_su_liq_ratio(
    lazy: pl.LazyFrame,
    col_qc1: str = COL_QC1_OS02,
    col_su_liq_ratio: str = COL_SU_LIQ_RATIO_OS02,
    max_su_liq_ratio: float = MAX_SU_LIQ_RATIO,
    *,
    envelope: str,
) -> pl.LazyFrame:

    match envelope:
        case "mean":
            epsilon = 0.00
        case "lower":
            epsilon = -SU_LIQ_RATIO_STD
        case "upper":
            epsilon = SU_LIQ_RATIO_STD
        case _:
            raise ValueError(
                f"invalid envelope choice, valid options are 'mean', 'lower' and "
                f"'upper'; got {envelope!r}"
            )

    return lazy.with_columns(
        (
            pl.when(pl.col(col_qc1) <= 6.5)
            .then(0.03 + 0.0143 * pl.col(col_qc1) + epsilon)
            .otherwise(float("nan"))
            .clip(upper_bound=max_su_liq_ratio)
        ).alias(col_su_liq_ratio)
    )


def add_os02_columns(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_qt: str,
    *,
    rolling_label: str,
    p_ref: float,
    envelope: str,
) -> pl.LazyFrame:
    return (
        lazy
        .pipe(compute_qc1, col_sv_eff, col_qt, rolling_label=rolling_label, p_ref=p_ref)
        .pipe(compute_su_liq_ratio, envelope=envelope)
    )  # fmt: off
