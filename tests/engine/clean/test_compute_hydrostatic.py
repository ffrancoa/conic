import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.engine._clean import compute_hydrostatic_column
from conic.workflow._defaults import COL_DEPTH, COL_U0, GAMMA_WATER


def _hydrostatic(lazy, *, water_level, gamma_water=GAMMA_WATER, **kwargs):
    return compute_hydrostatic_column(
        lazy,
        COL_DEPTH,
        COL_U0,
        water_level=water_level,
        gamma_water=gamma_water,
        **kwargs,
    )


def test_default_none():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0]})

    out_data = _hydrostatic(inp_data, water_level=None)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0]

    assert returned == expected


def test_intermediate_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = _hydrostatic(inp_data, water_level=1.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 5.0, 10.0]

    assert returned == expected


def test_surface_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = _hydrostatic(inp_data, water_level=0.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 5.0, 10.0, 15.0, 20.0]

    assert returned == expected


def test_below_level():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]})

    out_data = _hydrostatic(inp_data, water_level=5.0, gamma_water=10)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 0.0, 0.0]

    assert returned == expected


def test_custom_depth_col():
    inp_data = pl.LazyFrame({"Other...": [0.0, 0.5, 1.0]})

    out_data = compute_hydrostatic_column(
        inp_data, "Other...", COL_U0, water_level=0.0, gamma_water=GAMMA_WATER
    ).collect()

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 4.905, 9.810]

    assert returned == expected


def test_invalid_depth_col():
    data = pl.DataFrame({"z (m)": [0.0, 0.5, 1.0]})

    with pytest.raises(ColumnNotFoundError):
        _ = _hydrostatic(data, water_level=1.0)


def test_override_false():
    data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0], COL_U0: [0.0, 10.0, 20.0]})

    with pytest.raises(ValueError):
        _ = _hydrostatic(data, water_level=1.0)


def test_override_true():
    inp_data = pl.DataFrame({COL_DEPTH: [0.0, 0.5, 1.0], COL_U0: [0.0, 5.0, 10.0]})

    out_data = _hydrostatic(inp_data, water_level=0.5, override=True)

    returned = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 4.905]

    assert returned == expected
