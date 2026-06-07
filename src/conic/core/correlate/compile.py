from typing import Literal

import polars as pl

from conic.core.correlate import _olson2002, _robertson2021
from conic.engine._canonical import (
    COL_FR,
    COL_IC,
    COL_QC,
    COL_QTN,
    COL_SV_EFF,
    P_REF,
    ROLLING,
)


def add_r21_columns(
    lazy: pl.LazyFrame,
    *,
    col_fr: str = COL_FR,
    col_qtn: str = COL_QTN,
    col_ic: str = COL_IC,
) -> pl.LazyFrame:

    lazy = _robertson2021.compute_kc(lazy, col_ic=col_ic)
    lazy = _robertson2021.compute_qtncs(lazy, col_qtn=col_qtn)
    lazy = _robertson2021.compute_su_liq_ratio(lazy, col_fr=col_fr, col_ic=col_ic)

    return lazy


def add_os02_columns(
    lazy: pl.LazyFrame,
    bound: Literal["mean", "lower", "upper"],
    *,
    p_ref: float = P_REF,
    rolling: int = ROLLING,
    col_sv_eff: str = COL_SV_EFF,
    col_qc: str = COL_QC,
) -> pl.LazyFrame:

    lazy = _olson2002.compute_qc1(
        lazy, p_ref=p_ref, rolling=rolling, col_sv_eff=col_sv_eff, col_qc=col_qc
    )
    lazy = _olson2002.compute_su_liq_ratio(lazy, bound=bound)

    return lazy
