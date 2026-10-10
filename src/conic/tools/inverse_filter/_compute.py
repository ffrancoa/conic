import polars as pl

from conic._plugins import compute_qt_inv_plugin
from conic._utils import check_required_columns
from conic.tools.inverse_filter._columns import Columns
from conic.tools.inverse_filter._config import Config

COL_TEMP = "_temp"


def compute_inverse_filter(
    data: pl.DataFrame,
    *,
    config: Config | None = None,
    columns: Columns | None = None,
) -> pl.DataFrame:

    config = Config() if config is None else config
    columns = Columns() if columns is None else columns

    lazy = data.lazy()

    check_required_columns(
        lazy,
        {
            columns.depth,
            columns.qt,
            columns.fs,
            columns.fr,
            columns.sv_eff,
            columns.sv_tot,
        },
    )

    return (
        lazy.with_columns(
            compute_qt_inv_plugin(
                depth=columns.depth,
                qt=columns.qt,
                fs=columns.fs,
                fr=columns.fr,
                sv_eff=columns.sv_eff,
                sv_tot=columns.sv_tot,
                dc=config.dc,
                z50_ref=config.z50_ref,
                mz=config.mz,
                m50=config.m50,
                mq=config.mq,
                mt=config.mt,
                kernel_extent=config.kernel_extent,
                p_ref=config.p_ref,
                max_iter=config.max_iter,
                tolerance=config.tolerance,
            ).alias(COL_TEMP)
        )
        .with_columns(
            pl.col(COL_TEMP).struct.field("qt_inv").alias(columns.qt_inv),
            pl.col(COL_TEMP).struct.field("fs_inv").alias(columns.fs_inv),
            pl.col(COL_TEMP).struct.field("converged").alias(columns.convg),
        )
        .drop(COL_TEMP)
        .collect(engine="in-memory")
    )
