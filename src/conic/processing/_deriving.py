import polars as pl

from conic._plugins import compute_qtn_plugin
from conic._utils import check_required_columns

COL_TEMP = "_temp"


def _compute_cd_columns(
    lazy: pl.LazyFrame,
    col_fr: str,
    col_qtn: str,
    col_cd: str,
    col_ib: str,
) -> pl.LazyFrame:

    fr_column = pl.col(col_fr)
    qtn_column = pl.col(col_qtn)

    return lazy.with_columns(
        ((qtn_column - 11.0) * (1.0 + 0.06 * fr_column).pow(17))
        .clip(0.0, 140.0)
        .alias(col_cd),
        (100.0 * (qtn_column + 10.0) / (70.0 + qtn_column * fr_column))
        .alias(col_ib),
    )  # fmt: off


def _compute_qtn_columns(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_sv_tot: str,
    col_qt_rol: str,
    col_fr: str,
    col_n: str,
    col_qtn: str,
    col_ic: str,
    col_convg: str,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.LazyFrame:

    return (
        lazy.with_columns(
            compute_qtn_plugin(
                sv_eff=col_sv_eff,
                sv_tot=col_sv_tot,
                qt=col_qt_rol,
                fr=col_fr,
                p_ref=p_ref,
                max_iter=max_iter,
                tolerance=tolerance,
            ).alias(COL_TEMP)
        )
        .with_columns(
            pl.col(COL_TEMP).struct.field("n").alias(col_n),
            pl.col(COL_TEMP).struct.field("qtn").alias(col_qtn),
            pl.col(COL_TEMP).struct.field("ic").alias(col_ic),
            pl.col(COL_TEMP).struct.field("convg").alias(col_convg),
        )
        .drop(COL_TEMP)
    )


def compute_non_normalized_columns(
    lazy: pl.LazyFrame,
    col_sv_tot: str,
    col_u2: str,
    col_fs: str,
    col_qc: str,
    col_qt: str,
    col_qn: str,
    col_rf: str,
    *,
    area_ratio: float,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_fs, col_qc, col_u2})

    qt_column = pl.col(col_qc) + (1 - area_ratio) * (pl.col(col_u2) / 1000.0)

    return lazy.with_columns(
        qt_column
        .alias(col_qt),
        (qt_column - pl.col(col_sv_tot) / 1000.0)
        .alias(col_qn),
        (pl.col(col_fs) / (qt_column * 1000.0) * 100.0)
        .alias(col_rf),
    )  # fmt: off


def compute_rolling_columns(
    lazy: pl.LazyFrame,
    col_fs: str,
    col_qt: str,
    col_qn: str,
    *,
    rolling: int,
    rolling_label: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_fs, col_qt, col_qn})

    col_fs_rol = col_fs + rolling_label
    col_qt_rol = col_qt + rolling_label
    col_qn_rol = col_qn + rolling_label

    return lazy.with_columns(
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
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_u0: str,
    col_u2: str,
    col_fs: str,
    col_qn: str,
    col_qt1: str,
    col_fr: str,
    col_bq: str,
    col_u: str,
    *,
    rolling_label: str,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_sv_eff, col_fs, col_qn, col_u0, col_u2})

    col_fs_rol = col_fs + rolling_label
    col_qn_rol = col_qn + rolling_label

    qn_rol_kpa_column = pl.col(col_qn_rol) * 1000.0

    return (
        lazy.with_columns(
            (qn_rol_kpa_column / pl.col(col_sv_eff))
            .alias(col_qt1),
            (
                pl.when(pl.col(col_fs_rol) > 0.0)
                .then(100.0 * pl.col(col_fs_rol) / qn_rol_kpa_column)
                .otherwise(float("nan"))
            ).alias(col_fr),
            ((pl.col(col_u2) - pl.col(col_u0)) / qn_rol_kpa_column)
            .alias(col_bq),
        )
        .with_columns(
            (pl.col(col_qt1) * pl.col(col_bq))
            .alias(col_u),
        )
    )  # fmt: off


def compute_behavior_columns(
    lazy: pl.LazyFrame,
    col_sv_eff: str,
    col_sv_tot: str,
    col_qt_rol: str,
    col_fr: str,
    col_n: str,
    col_qtn: str,
    col_ic: str,
    col_convg: str,
    col_cd: str,
    col_ib: str,
    *,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_sv_eff, col_sv_tot, col_qt_rol, col_fr})

    return lazy.pipe(
        _compute_qtn_columns,
        col_sv_eff,
        col_sv_tot,
        col_qt_rol,
        col_fr,
        col_n,
        col_qtn,
        col_ic,
        col_convg,
        p_ref,
        max_iter,
        tolerance,
    ).pipe(_compute_cd_columns, col_fr, col_qtn, col_cd, col_ib)
