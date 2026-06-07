import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.core.calculate.prepare import compute_hydrostatic_column
from conic.engine._canonical import COL_DEPTH, COL_U0


def test_default_none():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0]})

    out_data = compute_hydrostatic_column(inp_data)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0]

    assert returned == expected


def test_intermediate_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = compute_hydrostatic_column(inp_data, water_level=1.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 5.0, 10.0]

    assert returned == expected


def test_surface_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = compute_hydrostatic_column(inp_data, water_level=0.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 5.0, 10.0, 15.0, 20.0]

    assert returned == expected


def test_below_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = compute_hydrostatic_column(inp_data, water_level=5.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 0.0, 0.0]

    assert returned == expected


def test_custom_depth_col():
    inp_data = pl.DataFrame({"Other...": [0.0, 0.5, 1.0]})

    out_data = compute_hydrostatic_column(
        inp_data, water_level=0.0, col_depth="Other..."
    )

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 4.905, 9.810]

    assert returned == expected


def test_invalid_depth_col():
    data = pl.DataFrame(
        {
            "z (m)": [0.0, 0.5, 1.0],
        }
    )

    with pytest.raises(ColumnNotFoundError):
        _ = compute_hydrostatic_column(data, water_level=1.0)


def test_override_false():
    data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0], COL_U0: [0.0, 10.0, 20.0]})

    with pytest.raises(ValueError):
        _ = compute_hydrostatic_column(data, water_level=1.0)


def test_override_true():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0], COL_U0: [0.0, 5.0, 10.0]})

    out_data = compute_hydrostatic_column(inp_data, water_level=0.5, override=True)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 4.905]

    assert returned == expected
