import math

import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.calculate.correlate import add_y14_columns
from conic.config._defaults import COL_FC_Y14, COL_FR, COL_IC


def _y14(ic, fr):
    inp_data = pl.LazyFrame(
        {COL_IC: ic, COL_FR: fr},
        schema_overrides={COL_IC: pl.Float64, COL_FR: pl.Float64},
    )
    out_data = add_y14_columns(inp_data, COL_IC, COL_FR, COL_FC_Y14).collect()
    return out_data[COL_FC_Y14].to_list()


def test_clean_sand():
    assert _y14([1.0], [1.0]) == [0.0]


def test_sandlike_sinusoidal():
    returned = _y14([2.0], [1.0])[0]
    expected = 42.0 * 2.0 - 55.0 + 10.0 * math.sin(math.pi * (2.0 - 2.50) / 1.19)
    assert returned == pytest.approx(expected)


def test_claylike_linear():
    returned = _y14([2.8], [1.0])[0]
    assert returned == pytest.approx(83.30 * 2.8 - 158.30)


def test_high_ic_capped():
    assert _y14([3.5], [1.0]) == [100.0]


def test_transition_low_fr():
    assert _y14([2.0], [0.4]) == [pytest.approx(2.0)]


def test_boundary_gap_is_nan():
    assert math.isnan(_y14([3.10], [1.0])[0])


def test_nan_ic_propagates():
    assert math.isnan(_y14([float("nan")], [1.0])[0])


def test_null_ic_yields_nan():
    assert math.isnan(_y14([None], [1.0])[0])


def test_missing_column_raises():
    inp_data = pl.LazyFrame({COL_IC: [2.0]})
    with pytest.raises(ColumnNotFoundError):
        add_y14_columns(inp_data, COL_IC, COL_FR, COL_FC_Y14).collect()
