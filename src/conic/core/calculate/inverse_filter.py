import polars as pl

from conic.core._plugins import inverse_filter_plugin
from conic.core._utils import check_required_columns

COL_TEMP = "_temp"


def compute_inverse_filter(
    lazy: pl.LazyFrame,
    col_qt: str,
    col_fs: str,
    col_fr: str,
    col_sv_eff: str,
    col_sv_tot: str,
    col_qt_inv: str,
    col_fs_inv: str,
    col_convg: str,
    *,
    dc: float,
    dz: float,
    z50_ref: float,
    mz: float,
    m50: float,
    mq: float,
    mt: float,
    p_ref: float,
    max_iter: int,
    tolerance: float,
    stall_tolerance: float,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_qt, col_fs, col_fr, col_sv_eff, col_sv_tot})

    return (
        lazy.with_columns(
            inverse_filter_plugin(
                qt=col_qt,
                fs=col_fs,
                fr=col_fr,
                sv_eff=col_sv_eff,
                sv_tot=col_sv_tot,
                dc=dc,
                dz=dz,
                z50_ref=z50_ref,
                mz=mz,
                m50=m50,
                mq=mq,
                mt=mt,
                p_ref=p_ref,
                max_iter=max_iter,
                tolerance=tolerance,
                stall_tolerance=stall_tolerance,
            ).alias(COL_TEMP)
        )
        .with_columns(
            pl.col(COL_TEMP).struct.field("qt_inv").alias(col_qt_inv),
            pl.col(COL_TEMP).struct.field("fs_inv").alias(col_fs_inv),
            pl.col(COL_TEMP).struct.field("converged").alias(col_convg),
        )
        .drop(COL_TEMP)
    )
