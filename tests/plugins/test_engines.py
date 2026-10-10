import math

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from conic._plugins import (
    compute_qc1n_plugin,
    compute_qtn_plugin,
    inverse_filter_plugin,
)
from conic.tools.inverse_filter import Config
from conic.workflow._defaults import (
    COL_DEPTH,
    COL_FC_BI14,
    COL_FR,
    COL_FS,
    COL_QT,
    COL_SV_EFF,
    COL_SV_TOT,
    MAX_ITER,
    P_REF,
    TOLERANCE,
)

N_ROWS = 600
N_CHUNKS = 3


def _sounding() -> pl.LazyFrame:
    depth = [0.5 + 0.02 * i for i in range(N_ROWS)]
    qt = [2.0 + 8.0 * (math.sin(z) > 0.5) + 0.5 * math.cos(3.0 * z) for z in depth]
    fs = [20.0 + 15.0 * math.sin(2.0 * z) for z in depth]
    sv_tot = [18.0 * z for z in depth]
    sv_eff = [s - 9.81 * max(z - 1.0, 0.0) for s, z in zip(sv_tot, depth, strict=True)]
    fr = [f / (q * 1000.0 - s) * 100.0 for f, q, s in zip(fs, qt, sv_tot, strict=True)]
    fc = [20.0 + 15.0 * math.cos(z) for z in depth]

    data = pl.DataFrame(
        {
            COL_DEPTH: depth,
            COL_QT: qt,
            COL_FS: fs,
            COL_FR: fr,
            COL_SV_EFF: sv_eff,
            COL_SV_TOT: sv_tot,
            COL_FC_BI14: fc,
        }
    )
    size = N_ROWS // N_CHUNKS
    chunks = [data.slice(k * size, size) for k in range(N_CHUNKS)]

    return pl.concat(chunks, rechunk=False).lazy()


def _inverse_filter_expr() -> pl.Expr:
    config = Config()

    return inverse_filter_plugin(
        COL_DEPTH,
        COL_QT,
        COL_FS,
        COL_FR,
        COL_SV_EFF,
        COL_SV_TOT,
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
    )


PLUGINS = {
    "compute_qtn": lambda: compute_qtn_plugin(
        COL_SV_EFF,
        COL_SV_TOT,
        COL_QT,
        COL_FR,
        p_ref=P_REF,
        max_iter=MAX_ITER,
        tolerance=TOLERANCE,
    ),
    "compute_qc1n": lambda: compute_qc1n_plugin(
        COL_SV_EFF,
        COL_QT,
        COL_FC_BI14,
        p_ref=P_REF,
        max_iter=MAX_ITER,
        tolerance=TOLERANCE,
    ),
    "inverse_filter": _inverse_filter_expr,
}


@pytest.mark.parametrize("plugin", PLUGINS.values(), ids=PLUGINS.keys())
def test_streaming_matches_in_memory(plugin):
    query = _sounding().select(plugin().alias("output")).unnest("output")

    returned = query.collect(engine="streaming")
    expected = query.collect(engine="in-memory")

    assert_frame_equal(returned, expected)
