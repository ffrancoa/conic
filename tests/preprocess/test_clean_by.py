import polars as pl

from conic._canonical import COL_DEPTH, COL_QC
from conic.processing.preprocess import clean_by_indicators


def test_replace():
    data = pl.DataFrame(
        {COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5], COL_QC: [0.3, 1.1, 1.2, -8888, 1.7]}
    )

    returned = clean_by_indicators(data, [-8888])
    expected = pl.DataFrame(
        {COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5], COL_QC: [0.3, 1.1, 1.2, None, 1.7]}
    )

    assert returned.equals(expected)


def test_remove():
    data = pl.DataFrame(
        {
            COL_DEPTH: [0.0, 0.5, 1.5, 2.0, 2.5],
            COL_QC: [-8888.0, 1.1, 1.2, -8888.0, 1.7],
        }
    )

    returned = clean_by_indicators(data, [-8888], mode="remove")
    expected = pl.DataFrame({COL_DEPTH: [0.5, 1.5, 2.5], COL_QC: [1.1, 1.2, 1.7]})

    assert returned.equals(expected)
