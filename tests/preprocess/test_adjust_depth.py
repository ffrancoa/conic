import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.preprocess import adjust_depth_spacing
from conic._canonical import COL_DEPTH


def test_invalid_depth_col():
    data = pl.DataFrame({
            "z (m)": [0.0, 0.5, 1.0]
        })

    with pytest.raises(ColumnNotFoundError):
        _ = adjust_depth_spacing(data)

def test_invalid_mutual_arguments():
    data = pl.DataFrame({
            COL_DEPTH: [0.03, 0.05, 0.07, 0.10]
        })

    with pytest.raises(ValueError):
        _ = adjust_depth_spacing(data)

def test_too_few_rows():
    data = pl.DataFrame({
            COL_DEPTH: [0.05]
        })

    with pytest.raises(ValueError):
        _ = adjust_depth_spacing(data, start_depth=0.05)

def test_start_depth_and_spacing():
    inp_data = pl.DataFrame({
            COL_DEPTH: [0.03, 0.05, 0.07, 0.10]
        })

    out_data = adjust_depth_spacing(inp_data, start_depth=0.025, spacing=0.025)

    returned = out_data[COL_DEPTH].to_list()
    expected = [0.025, 0.05, 0.075, 0.10]

    assert returned == expected

def test_spacing_only():
    inp_data = pl.DataFrame({
            COL_DEPTH: [0.05, 0.07, 0.10, 0.13]
        })

    out_data = adjust_depth_spacing(inp_data, spacing=0.025)

    returned = out_data[COL_DEPTH].to_list()
    expected = [0.05, 0.075, 0.10, 0.125]

    assert returned == expected
