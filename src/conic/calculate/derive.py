import polars as pl
from polars.exceptions import ColumnNotFoundError

from conic.calculate._plugins import compute_behavior_plugin
from conic.calculate._utils import get_missing_columns
from conic.prelude._canonical import (
    COL_BQ,
    COL_CD,
    COL_CONVG,
    COL_FR,
    COL_FS,
    COL_IB,
    COL_IC,
    COL_N,
    COL_QC,
    COL_QN,
    COL_QT,
    COL_QT1,
    COL_QTN,
    COL_RF,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U,
    COL_U0,
    COL_U2,
    MAX_ITER,
    P_REF,
    ROLLING,
    ROLLING_LABEL,
    TOLERANCE,
)


def compute_non_normalized_columns(
    data: pl.LazyFrame,
    area_ratio: float,
    *,
    col_sv_tot: str = COL_SV_TOT,
    col_u2: str = COL_U2,
    col_fs: str = COL_FS,
    col_qc: str = COL_QC,
    col_qt: str = COL_QT,
    col_qn: str = COL_QN,
    col_rf: str = COL_RF,
) -> pl.LazyFrame:

    if missing_columns := get_missing_columns(data, {col_fs, col_qc, col_u2}):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    col_qt_mpa = pl.col(col_qc) + (1 - area_ratio) * (pl.col(col_u2) / 1000.0)

    return data.with_columns(
        col_qt_mpa.alias(col_qt),
        (col_qt_mpa - pl.col(col_sv_tot) / 1000.0).alias(col_qn),
        (pl.col(col_fs) / (col_qt_mpa * 1000.0) * 100.0).alias(col_rf),
    )


def compute_rolling_columns(
    data: pl.LazyFrame,
    rolling: int = ROLLING,
    *,
    col_fs: str = COL_FS,
    col_qt: str = COL_QT,
    col_qn: str = COL_QN,
    rolling_label: str = ROLLING_LABEL,
) -> pl.LazyFrame:

    col_fs_rol = col_fs + rolling_label
    col_qt_rol = col_qt + rolling_label
    col_qn_rol = col_qn + rolling_label

    if missing_columns := get_missing_columns(data, {col_fs, col_qt, col_qn}):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

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
        (
            pl.col(col_qn)
            .rolling_mean(window_size=rolling, min_samples=rolling, center=True)
            .fill_null(float("nan"))
        ).alias(col_qn_rol),
    )


def compute_normalized_columns(
    data: pl.LazyFrame,
    *,
    col_sv_eff: str = COL_SV_EFF,
    col_u0: str = COL_U0,
    col_u2: str = COL_U2,
    col_fs: str = COL_FS,
    col_qn: str = COL_QN,
    col_qt1: str = COL_QT1,
    col_fr: str = COL_FR,
    col_bq: str = COL_BQ,
    col_u: str = COL_U,
    rolling_label: str = ROLLING_LABEL,
) -> pl.LazyFrame:

    required_columns = {col_sv_eff, col_fs, col_qn, col_u0, col_u2}

    if missing_columns := get_missing_columns(data, required_columns):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    col_fs_rol = col_fs + rolling_label
    col_qn_rol = col_qn + rolling_label

    col_qn_rol_kpa = pl.col(col_qn_rol) * 1000.0

    return data.with_columns(
        (col_qn_rol_kpa / pl.col(col_sv_eff)).alias(col_qt1),
        (100.0 * pl.col(col_fs_rol) / col_qn_rol_kpa).alias(col_fr),
        ((pl.col(col_u2) - pl.col(col_u0)) / col_qn_rol_kpa).alias(col_bq),
    ).with_columns((pl.col(col_qt1) * pl.col(col_bq)).alias(col_u))


def compute_behavior_columns(
    data: pl.LazyFrame,
    *,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    col_qt: str = COL_QT,
    col_fr: str = COL_FR,
    col_n: str = COL_N,
    col_qtn: str = COL_QTN,
    col_ic: str = COL_IC,
    col_convg: str = COL_CONVG,
    col_cd: str = COL_CD,
    col_ib: str = COL_IB,
    p_ref: float = P_REF,
    max_iter: int = MAX_ITER,
    tolerance: float = TOLERANCE,
    rolling_label: str = ROLLING_LABEL,
) -> pl.LazyFrame:

    required_columns = {col_sv_eff, col_sv_tot, col_qt, col_fr}

    if missing_columns := get_missing_columns(data, required_columns):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    return (
        data.with_columns(
            compute_behavior_plugin(
                sv_eff=col_sv_eff,
                sv_tot=col_sv_tot,
                qt=(col_qt + rolling_label),
                fr=col_fr,
                p_ref=p_ref,
                max_iter=max_iter,
                tolerance=tolerance,
            ).alias("_temp")
        )
        .with_columns(
            pl.col("_temp").struct.field("n").alias(col_n),
            pl.col("_temp").struct.field("qtn").alias(col_qtn),
            pl.col("_temp").struct.field("ic").alias(col_ic),
            pl.col("_temp").struct.field("convg").alias(col_convg),
            pl.col("_temp").struct.field("cd").alias(col_cd),
            pl.col("_temp").struct.field("ib").alias(col_ib),
        )
        .drop("_temp")
    )
