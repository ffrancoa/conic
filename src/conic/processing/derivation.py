import polars as pl

from polars.exceptions import ColumnNotFoundError

from conic._canonical import (
    COL_BQ,
    COL_FR,
    COL_FS,
    COL_QC,
    COL_QT,
    COL_QT1,
    COL_RF,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    ROLLING,
    ROLLING_LABEL,
)
from conic.processing._helpers import get_missing_columns


def _convert_mpa_to_kpa(column_name: str) -> pl.Expr:
    return pl.col(column_name) * 1000.0


def compute_non_normalized(
    data: pl.DataFrame,
    area_ratio: float,
    *,
    col_fs: str = COL_FS,
    col_qc: str = COL_QC,
    col_u2: str = COL_U2,
    col_qt: str = COL_QT,
    col_rf: str = COL_RF,
) -> pl.DataFrame:

    if missing_columns := get_missing_columns(data, {col_fs, col_qc, col_u2}):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    return data.with_columns(
        (
            qt_mpa_expr := pl.col(col_qc) + (1 - area_ratio) * (pl.col(col_u2) / 1000.0)
        ).alias(col_qt),
        (
            pl.col(col_fs) / (qt_mpa_expr * 1000.0) * 100.0
        ).alias(col_rf),
    )


def compute_rolling_columns(
    data: pl.DataFrame,
    rolling: int = ROLLING,
    *,
    col_fs: str = COL_FS,
    col_qt: str = COL_QT,
    rolling_label: str = ROLLING_LABEL,
) -> pl.DataFrame:

    col_fs_rol = col_fs + rolling_label
    col_qt_rol = col_qt + rolling_label

    if missing_columns := get_missing_columns(data, {col_fs, col_qt}):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    return data.with_columns(
        (
            pl.col(col_fs)
            .rolling_mean(window_size=rolling, min_samples=rolling, center=True)
            .fill_null(float("nan"))
        ).alias(col_fs_rol),
        (
            pl.col(col_qt)
            .rolling_mean(window_size=rolling, min_samples=rolling, center=True)
            .fill_null(float("nan"))
        ).alias(col_qt_rol),
    )


def compute_normalized(
    data: pl.DataFrame,
    *,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    col_fs: str = COL_FS,
    col_qt: str = COL_QT,
    col_u0: str = COL_U0,
    col_u2: str = COL_U2,
    col_qt1: str = COL_QT1,
    col_fr: str = COL_FR,
    col_bq: str = COL_BQ,
    rolling_label: str = ROLLING_LABEL,
) -> pl.DataFrame:

    required_columns = {col_sv_eff, col_sv_tot, col_fs, col_qt, col_u0, col_u2}

    if missing_columns := get_missing_columns(data, required_columns):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    col_fs_rol = col_fs + rolling_label
    col_qt_rol = col_qt + rolling_label

    qt_rol_kpa_expr = _convert_mpa_to_kpa(col_qt_rol)

    return data.with_columns(
        (
            (qt_rol_kpa_expr - pl.col(col_sv_tot)) / pl.col(col_sv_eff)
        ).alias(col_qt1),
        (
            pl.col(col_fs_rol) / (qt_rol_kpa_expr - pl.col(col_sv_tot)) * 100.0
        ).alias(col_fr),
        (
            (pl.col(col_u2) - pl.col(col_u0)) / (qt_rol_kpa_expr - pl.col(col_sv_tot))
        ).alias(col_bq),
    )
