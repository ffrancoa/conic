from pathlib import Path

import polars as pl
from polars.plugins import register_plugin_function

LIB_PATH = Path(__file__).parent.parent

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
