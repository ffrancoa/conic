import polars as pl

from conic._utils import check_required_columns
from conic.calculate.calibrate._result import CalibrationResult

SLOPE: float = 80.0
INTERCEPT: float = 137.0


def calibrate_bi14(
    lazy: pl.LazyFrame,
    col_ic: str,
    col_fc: str,
) -> CalibrationResult:

    check_required_columns(lazy, {col_ic, col_fc})

    response = pl.col(col_ic) - pl.col(col_fc) / SLOPE

    stats = (
        lazy.filter(pl.col(col_ic).is_finite() & pl.col(col_fc).is_finite())
        .select(
            mean=response.mean(),
            std=response.std(),
            n=response.len(),
        )
        .collect()
    )

    n_points = stats["n"][0]

    if n_points < 2:
        raise ValueError(
            "at least two valid (Ic, FC) pairs are required for calibration"
        )

    return CalibrationResult(
        coefficient=-stats["mean"][0] + INTERCEPT / SLOPE,
        residual_std=stats["std"][0],
        n_points=n_points,
    )
