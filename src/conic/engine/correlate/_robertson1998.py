import polars as pl

from conic._utils import check_required_columns

IC_CLEANSAND_THRESHOLD: float = 1.26
IC_CLAYLIKE_THRESHOLD: float = 3.50

IC_TRANSITION_LOWER: float = 1.64
IC_TRANSITION_UPPER: float = 2.36
FR_TRANSITION_THRESHOLD: float = 0.50
FC_TRANSITION: float = 5.0


def add_rw98_columns(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_fr: str,
    col_fc: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_ic, col_fr})

    ic = pl.col(col_ic)
    fr = pl.col(col_fr)

    fc_claylike_column = 1.75 * ic.pow(3.25) - 3.70

    transition_column = (
        (ic > IC_TRANSITION_LOWER)
        & (ic < IC_TRANSITION_UPPER)
        & (fr < FR_TRANSITION_THRESHOLD)
    )

    return lazy.with_columns(
        (
            pl.when(ic.is_nan())
            .then(float("nan"))
            .when(transition_column)
            .then(FC_TRANSITION)
            .when(ic < IC_CLEANSAND_THRESHOLD)
            .then(0.0)
            .when(ic <= IC_CLAYLIKE_THRESHOLD)
            .then(fc_claylike_column)
            .when(ic > IC_CLAYLIKE_THRESHOLD)
            .then(100.0)
            .otherwise(float("nan"))
        ).alias(col_fc)
    )
