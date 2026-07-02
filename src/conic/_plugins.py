from pathlib import Path

import polars as pl
from polars.plugins import register_plugin_function

LIB_PATH = Path(__file__).parent

type IntoExprColumn = pl.Expr | str | pl.Series


def compute_qtn_plugin(
    sv_eff: IntoExprColumn,
    sv_tot: IntoExprColumn,
    qt: IntoExprColumn,
    fr: IntoExprColumn,
    *,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.Expr:

    return register_plugin_function(
        function_name="compute_qtn",
        plugin_path=LIB_PATH,
        args=[sv_eff, sv_tot, qt, fr],
        kwargs={"p_ref": p_ref, "max_iter": max_iter, "tolerance": tolerance},
        is_elementwise=True,
    )


def inverse_filter_plugin(
    qt: IntoExprColumn,
    fs: IntoExprColumn,
    fr: IntoExprColumn,
    sv_eff: IntoExprColumn,
    sv_tot: IntoExprColumn,
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
) -> pl.Expr:

    return register_plugin_function(
        function_name="inverse_filter",
        plugin_path=LIB_PATH,
        args=[qt, fs, fr, sv_eff, sv_tot],
        kwargs={
            "dc": dc,
            "dz": dz,
            "z50_ref": z50_ref,
            "mz": mz,
            "m50": m50,
            "mq": mq,
            "mt": mt,
            "p_ref": p_ref,
            "max_iter": max_iter,
            "tolerance": tolerance,
            "stall_tolerance": stall_tolerance,
        },
        is_elementwise=False,
    )


def compute_qc1n_plugin(
    sv_eff: IntoExprColumn,
    qt: IntoExprColumn,
    fc: IntoExprColumn,
    *,
    p_ref: float,
    max_iter: int,
    tolerance: float,
) -> pl.Expr:

    return register_plugin_function(
        function_name="compute_qc1n",
        plugin_path=LIB_PATH,
        args=[sv_eff, qt, fc],
        kwargs={"p_ref": p_ref, "max_iter": max_iter, "tolerance": tolerance},
        is_elementwise=True,
    )
