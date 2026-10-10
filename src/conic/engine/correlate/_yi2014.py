import math

import polars as pl

from conic._utils import check_required_columns

IC_CLEANSAND_THRESHOLD: float = 1.31
IC_LINEAR_THRESHOLD: float = 2.50
IC_CLAYLIKE_THRESHOLD: float = 3.10

IC_TRANSITION_LOWER: float = 1.31
IC_TRANSITION_UPPER: float = 2.36
FR_TRANSITION_THRESHOLD: float = 0.60


def add_y14_columns(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_fr: str,
    col_fc: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_ic, col_fr})

    ic = pl.col(col_ic)
    fr = pl.col(col_fr)

    fc_sandlike_column = (
        42.0 * ic - 55.0
        + 10.0 * (math.pi * (ic - IC_LINEAR_THRESHOLD) / 1.19).sin()
    )  # fmt: off
    fc_claylike_column = 83.30 * ic - 158.30

    transition_column = (
        (ic > IC_TRANSITION_LOWER)
        & (ic <= IC_TRANSITION_UPPER)
        & (fr < FR_TRANSITION_THRESHOLD)
    )

    return lazy.with_columns(
        (
            pl.when(ic.is_nan())
            .then(float("nan"))
            .when(transition_column)
            .then(5.0 * fr)
            .when(ic < IC_CLEANSAND_THRESHOLD)
            .then(0.0)
            .when(ic < IC_LINEAR_THRESHOLD)
            .then(fc_sandlike_column)
            .when(ic < IC_CLAYLIKE_THRESHOLD)
            .then(fc_claylike_column)
            .when(ic > IC_CLAYLIKE_THRESHOLD)
            .then(100.0)
            .otherwise(float("nan"))
        ).alias(col_fc)
    )
