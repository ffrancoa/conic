import polars as pl

from conic._plugins import compute_qc1n_plugin
from conic._utils import check_required_columns

COL_TEMP = "_temp"

FC_STD: float = 0.29
DEFAULT_ENVELOPE: str = "mean"
ENVELOPE_MAP: dict[str, float] = {
    "mean": 0.00,
    "lower": -FC_STD,
    "upper": FC_STD,
}


def compute_fc(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_fc: str,
    *,
    envelope: str | None,
    fitting_term: float | None,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_ic})

    if (envelope is None) == (fitting_term is None):
        raise ValueError("exactly one of 'envelope' or 'fitting_term' must be provided")

    if envelope is not None:
        if envelope not in ENVELOPE_MAP:
            raise ValueError(
                f"invalid envelope choice, valid options are {sorted(ENVELOPE_MAP)}; "
                f"got {envelope!r}"
            )
        fitting_term = ENVELOPE_MAP[envelope]

    fc_column = 80.0 * (pl.col(col_ic) + fitting_term) - 137.0

    return lazy.with_columns(fc_column.clip(0.0, 100.0).alias(col_fc))


def compute_qc1n_columns(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_qt_rol: str,
    col_fc: str,
    col_m: str,
    col_qc1n: str,
    col_qc1ncs: str,
    col_convg: str,
    *,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.LazyFrame:

    return (
        lazy.with_columns(
            compute_qc1n_plugin(
                sv_eff=col_sv_eff,
                qt=col_qt_rol,
                fc=col_fc,
                p_ref=p_ref,
                max_iter=max_iter,
                tolerance=tolerance,
            ).alias(COL_TEMP)
        )
        .with_columns(
            pl.col(COL_TEMP).struct.field("m").alias(col_m),
            pl.col(COL_TEMP).struct.field("qc1n").alias(col_qc1n),
            pl.col(COL_TEMP).struct.field("qc1ncs").alias(col_qc1ncs),
            pl.col(COL_TEMP).struct.field("convg").alias(col_convg),
        )
        .drop(COL_TEMP)
    )


def add_bi14_columns(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_sv_eff: str,
    col_qt_rol: str,
    col_fc: str,
    col_m: str,
    col_qc1n: str,
    col_qc1ncs: str,
    col_convg: str,
    *,
    envelope: str | None = None,
    fitting_term: float | None = None,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.LazyFrame:
    return (
        lazy
        .pipe(compute_fc, col_ic, col_fc, envelope=envelope, fitting_term=fitting_term)
        .pipe(
            compute_qc1n_columns, col_sv_eff, col_qt_rol, col_fc,
            col_m, col_qc1n, col_qc1ncs, col_convg,
            p_ref=p_ref, max_iter=max_iter, tolerance=tolerance,
        )
    )  # fmt: off
