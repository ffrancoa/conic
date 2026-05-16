import polars as pl

from conic.preprocess import replace_indicators
from conic._canonical import COL_DEPTH, COL_QC

def test_replace_default_value():
    data = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [0.3, 1.1, 1.2, -8888, 1.7]
        })

    returned = replace_indicators(data, [-8888])
    expected = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [0.3, 1.1, 1.2, None, 1.7]
        })

    assert returned.equals(expected)

def test_replace_custom_value():
    data = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [0.3, 1.1, 1.2, -8888, 1.7]
        })

    returned = replace_indicators(data, [-8888], value=-999)
    expected = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [0.3, 1.1, 1.2, -999.0, 1.7]
        })

    assert returned.equals(expected)

