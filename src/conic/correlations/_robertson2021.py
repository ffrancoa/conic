import polars as pl

from conic._utils import check_required_columns

IC_CLEANSAND_THRESHOLD: float = 1.7
IC_SANDLIKE_THRESHOLD: float = 2.6
IC_CLAYLIKE_THRESHOLD: float = 3.0

MAX_SU_LIQ_RATIO: float = 0.25


def compute_kc(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_kc: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_ic})

    kc_transitional_column = (
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
            .otherwise(kc_transitional_column)
        ).alias(col_kc)
    )


def compute_qtncs(
    lazy: pl.LazyFrame,
    col_qtn: str,
    col_kc: str,
    col_qtncs: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_qtn})

    return lazy.with_columns((pl.col(col_qtn) * pl.col(col_kc)).alias(col_qtncs))


def compute_su_liq_ratio(
    lazy: pl.LazyFrame,
    col_fr: str,
    col_ic: str,
    col_qtncs: str,
    col_su_liq_ratio: str,
    *,
    max_su_liq_ratio: float,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_fr})

    su_liq_claylike_column = pl.col(col_fr) * pl.col(col_qtncs)
    su_liq_sandlike_column = (
        0.0007 * (0.084 * pl.col(col_qtncs)).exp() + 0.3 / pl.col(col_qtncs)
    )  # fmt: off

    return lazy.with_columns(
        (
            pl.when(pl.col(col_ic) >= IC_CLAYLIKE_THRESHOLD)
            .then(su_liq_claylike_column)
            .when(pl.col(col_qtncs) <= 20.0)
            .then(0.02)
            .when(pl.col(col_qtncs) >= 80.0)
            .then(float("nan"))
            .otherwise(su_liq_sandlike_column)
            .clip(upper_bound=max_su_liq_ratio)
        ).alias(col_su_liq_ratio)
    )


def add_r21_columns(
    lazy: pl.LazyFrame,
    col_fr: str,
    col_qtn: str,
    col_ic: str,
    col_kc: str,
    col_qtncs: str,
    col_su_liq_ratio: str,
    *,
    max_su_liq_ratio: float,
) -> pl.LazyFrame:
    return (
        lazy
        .pipe(compute_kc, col_ic, col_kc)
        .pipe(compute_qtncs, col_qtn, col_kc, col_qtncs)
        .pipe(
            compute_su_liq_ratio, col_fr, col_ic, col_qtncs, col_su_liq_ratio,
            max_su_liq_ratio=max_su_liq_ratio,
        )
    )  # fmt: off
