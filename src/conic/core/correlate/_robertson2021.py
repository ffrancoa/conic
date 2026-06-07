import polars as pl
from polars.exceptions import ColumnNotFoundError

from conic.core._utils import get_column_names

COL_KC_R21: str = "Kc (-) [R21]"
COL_QTNCS_R21: str = "Qtn,cs (-) [R21]"
COL_SU_LIQ_RATIO_R21: str = "Su_liq (-) [R21]"

IC_CLEANSAND_THRESHOLD: float = 1.7
IC_SANDLIKE_THRESHOLD: float = 2.6
IC_CLAYLIKE_THRESHOLD: float = 3.0

MAX_SU_LIQ_RATIO: float = 0.25


def compute_kc(
    lazy: pl.LazyFrame,
    *,
    col_ic: str,
    col_kc: str = COL_KC_R21,
) -> pl.LazyFrame:

    if col_ic not in get_column_names(lazy):
        raise ColumnNotFoundError(f"ic column is missing in DataFrame: '{col_ic}'.")

    kc_transitional = (
        1.8346 * pl.col(col_ic).pow(5)
        - 23.673 * pl.col(col_ic).pow(4)
        + 124.020 * pl.col(col_ic).pow(3)
        - 320.616 * pl.col(col_ic).pow(2)
        + 405.821 * pl.col(col_ic)
        - 199.970
    )

    return lazy.with_columns(
        (
            pl.when(pl.col(col_ic) <= IC_CLEANSAND_THRESHOLD)
            .then(1.0)
            .when(pl.col(col_ic) >= IC_CLAYLIKE_THRESHOLD)
            .then(float("nan"))
            .otherwise(kc_transitional)
        ).alias(col_kc)
    )


def compute_qtncs(
    lazy: pl.LazyFrame,
    *,
    col_qtn: str,
    col_kc: str = COL_KC_R21,
    col_qtncs: str = COL_QTNCS_R21,
) -> pl.LazyFrame:

    if col_qtn not in get_column_names(lazy):
        raise ColumnNotFoundError(f"qtn column is missing in DataFrame: '{col_qtn}'.")

    return lazy.with_columns((pl.col(col_qtn) * pl.col(col_kc)).alias(col_qtncs))


def compute_su_liq_ratio(
    lazy: pl.LazyFrame,
    *,
    col_fr: str,
    col_ic: str,
    col_qtncs: str = COL_QTNCS_R21,
    col_su_liq_ratio: str = COL_SU_LIQ_RATIO_R21,
    max_su_liq_ratio: float = MAX_SU_LIQ_RATIO,
) -> pl.LazyFrame:

    if col_fr not in get_column_names(lazy):
        raise ColumnNotFoundError(f"fr column is missing in DataFrame: '{col_fr}'.")

    su_liq_claylike = pl.col(col_fr) * pl.col(col_qtncs)
    su_liq_sandlike = (
        0.0007 * (0.084 * pl.col(col_qtncs)).exp() + 0.3 / pl.col(col_qtncs)
    )  # fmt: off

    return lazy.with_columns(
        (
            pl.when(pl.col(col_ic) >= IC_CLAYLIKE_THRESHOLD)
            .then(su_liq_claylike)
            .when(pl.col(col_qtncs) <= 20.0)
            .then(0.02)
            .when(pl.col(col_qtncs) >= 80.0)
            .then(float("nan"))
            .otherwise(su_liq_sandlike)
            .clip(upper_bound=max_su_liq_ratio)
        ).alias(col_su_liq_ratio)
    )
