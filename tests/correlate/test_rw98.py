import math

import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.calculate.correlate import add_rw98_columns
from conic.workflow._defaults import COL_FC_RW98, COL_FR, COL_IC


def _rw98(ic, fr):
    inp_data = pl.LazyFrame(
        {COL_IC: ic, COL_FR: fr},
        schema_overrides={COL_IC: pl.Float64, COL_FR: pl.Float64},
    )
    out_data = add_rw98_columns(inp_data, COL_IC, COL_FR, COL_FC_RW98).collect()
    return out_data[COL_FC_RW98].to_list()


def test_clean_sand():
    assert _rw98([1.0], [1.0]) == [0.0]


def test_claylike_polynomial():
    returned = _rw98([2.0], [1.0])[0]
    expected = 1.75 * 2.0**3.25 - 3.70
    assert returned == pytest.approx(expected)


def test_high_ic_capped():
    assert _rw98([4.0], [1.0]) == [100.0]


def test_transition_low_fr():
    assert _rw98([2.0], [0.4]) == [5.0]


def test_transition_ignored_when_fr_high():
    returned = _rw98([2.0], [0.6])[0]
    assert returned == pytest.approx(1.75 * 2.0**3.25 - 3.70)


def test_nan_ic_propagates():
    assert math.isnan(_rw98([float("nan")], [1.0])[0])


def test_null_ic_yields_nan():
    assert math.isnan(_rw98([None], [1.0])[0])


def test_missing_column_raises():
    inp_data = pl.LazyFrame({COL_IC: [2.0]})
    with pytest.raises(ColumnNotFoundError):
        add_rw98_columns(inp_data, COL_IC, COL_FR, COL_FC_RW98).collect()
