import polars as pl

from conic.engine._clean import clean_by_indicators
from conic.workflow._defaults import COL_DEPTH, COL_QC


def test_replace():
    data = pl.LazyFrame(
        {COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5], COL_QC: [0.3, 1.1, 1.2, -8888, 1.7]}
    )

    returned = clean_by_indicators(data, indicators=[-8888], mode="replace").collect()
    expected = pl.DataFrame(
        {
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [0.3, 1.1, 1.2, float("nan"), 1.7],
        }
    )

    assert returned.equals(expected)


def test_remove():
    data = pl.LazyFrame(
        {
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [-8888.0, 1.1, 1.2, -8888.0, 1.7],
        }
    )

    returned = clean_by_indicators(data, indicators=[-8888], mode="remove").collect()
    expected = pl.DataFrame({COL_DEPTH: [0.5, 1.5, 2.5], COL_QC: [1.1, 1.2, 1.7]})

    assert returned.equals(expected)
