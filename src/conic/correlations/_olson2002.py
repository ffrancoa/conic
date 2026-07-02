import polars as pl

from conic.core._utils import check_required_columns

DEFAULT_ENVELOPE: str = "mean"
MAX_SU_LIQ_RATIO: float = 0.15
SU_LIQ_RATIO_STD: float = 0.03

ENVELOPE_MAP: dict[str, float] = {
    "mean": 0.00,
    "lower": -SU_LIQ_RATIO_STD,
    "upper": SU_LIQ_RATIO_STD,
}


def compute_qc1(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_qt_rol: str,
    col_qc1: str,
    *,
    p_ref: float,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_sv_eff, col_qt_rol})

    return lazy.with_columns(
        (
            (1.8 * pl.col(col_qt_rol)) / (0.8 + (pl.col(col_sv_eff) / p_ref))
        ).alias(col_qc1)
    )  # fmt: off


def compute_su_liq_ratio(
    lazy: pl.LazyFrame,
    col_qc1: str,
    col_su_liq_ratio: str,
    *,
    envelope: str,
    max_su_liq_ratio: float,
) -> pl.LazyFrame:

    if envelope not in ENVELOPE_MAP:
        raise ValueError(
            f"invalid envelope choice, valid options are "
            f"{sorted(ENVELOPE_MAP)}; got {envelope!r}"
        )

    epsilon = ENVELOPE_MAP[envelope]

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
    col_qt_rol: str,
    col_qc1: str,
    col_su_liq_ratio: str,
    *,
    p_ref: float,
    envelope: str,
    max_su_liq_ratio: float,
) -> pl.LazyFrame:
    return (
        lazy
        .pipe(compute_qc1, col_sv_eff, col_qt_rol, col_qc1, p_ref=p_ref)
        .pipe(
            compute_su_liq_ratio, col_qc1, col_su_liq_ratio,
            envelope=envelope, max_su_liq_ratio=max_su_liq_ratio,
        )
    )  # fmt: off
