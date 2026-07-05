import polars as pl
import polars.selectors as cs

from conic.calculate._clean import (
    _remove_rows_with_indicators,
)
from conic.config._defaults import COL_DEPTH, COL_QC


def test_remove_rows():
    data = pl.DataFrame(
        {COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0], COL_QC: [-999.0, 1.2, -999.0, 0.8, 1.6]}
    )

    returned = _remove_rows_with_indicators(data, cs.numeric(), [-999])
    expected = pl.DataFrame({COL_DEPTH: [0.5, 1.5, 2.0], COL_QC: [1.2, 0.8, 1.6]})

    assert returned.equals(expected)
