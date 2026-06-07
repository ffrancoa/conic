import polars as pl

from conic.core.calculate.prepare import split_by_indicators
from conic.engine._canonical import COL_DEPTH, COL_QC


def test_full_behavior():
    data = pl.DataFrame(
        {
            COL_DEPTH: [0.25, 0.50, 0.75, 1.00, 1.25],
            COL_QC: [0.3, -7777, 0.9, 1.2, -8888],
        }
    )

    returned = split_by_indicators(data, [-8888, -7777], index_col="index")
    expected = [
        pl.DataFrame(
            {"index": [1, 4], COL_DEPTH: [0.50, 1.25], COL_QC: [-7777, -8888]}
        ),
        pl.DataFrame(
            {"index": [0, 2, 3], COL_DEPTH: [0.25, 0.75, 1.00], COL_QC: [0.3, 0.9, 1.2]}
        ),
    ]

    for rows_returned, rows_expected in zip(returned, expected, strict=True):
        assert rows_returned.equals(rows_expected)
