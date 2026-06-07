import polars as pl
import pytest

from conic.core.calculate.prepare import filter_by_indicators
from conic.engine._canonical import COL_DEPTH, COL_QC


def test_remove_rows():
    data = pl.DataFrame(
        {COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0], COL_QC: [-999.0, 1.2, -999.0, 0.8, 1.6]}
    )

    returned = filter_by_indicators(data, [-999])
    expected = pl.DataFrame({COL_DEPTH: [0.5, 1.5, 2.0], COL_QC: [1.2, 0.8, 1.6]})

    assert returned.equals(expected)


def test_keep_rows():
    data = pl.DataFrame(
        {COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0], COL_QC: [-999.0, 1.2, -999.0, 0.8, 1.6]}
    )

    returned = filter_by_indicators(data, [-999], action="select")
    expected = pl.DataFrame({COL_DEPTH: [0.0, 1.0], COL_QC: [-999, -999]})

    assert returned.equals(expected)


def test_invalid_action():
    data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0], COL_QC: [0.5, 1.2, -999.0]})

    with pytest.raises(ValueError):
        _ = filter_by_indicators(data, indicators=[-999], action="keep")
