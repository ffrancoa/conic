import polars as pl
import pytest
from polars import exceptions as pe

from conic.preprocess import compute_hydrostatic
from conic._canonical import COL_DEPTH, COL_U0

def test_intermediate_level():
    inp_data = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]
        })
    
    out_data = compute_hydrostatic(inp_data, water_level=1.0, gamma_water=10)
            
    result = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 5.0, 10.0]

    assert result == expected

def test_surface_level():
    inp_data = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]
        })
    
    out_data = compute_hydrostatic(inp_data, water_level=0.0, gamma_water=10)
            
    result = out_data[COL_U0].to_list()
    expected = [0.0, 5.0, 10.0, 15.0, 20.0]

    assert result == expected

def test_below_level():
    inp_data = pl.DataFrame({
            COL_DEPTH: [0.0, 0.5, 1.0, 1.5, 2.0]
        })
    
    out_data = compute_hydrostatic(inp_data, water_level=5.0, gamma_water=10)
            
    result = out_data[COL_U0].to_list()
    expected = [0.0, 0.0, 0.0, 0.0, 0.0]

    assert result == expected

def test_missing_depth_col():
    inp_data = pl.DataFrame({
        "Other...": [0.0, 0.5, 1.0]
    })

    with pytest.raises(pe.ColumnNotFoundError):
        _ = compute_hydrostatic(inp_data, water_level=0.0)
    
def test_custom_depth_col():
    inp_data = pl.DataFrame({
        "Other...": [0.0, 0.5, 1.0]
    })

    out_data = compute_hydrostatic(inp_data, water_level=0.0, col_depth="Other...")

    result = out_data[COL_U0].to_list()
    expected = [.0, 4.905, 9.810]

    assert result == expected

def test_override_false():
    inp_data = pl.DataFrame({
        COL_DEPTH: [0.0, 0.5, 1.0],
        COL_U0: [0.0, 10.0, 20.0]
    })

    with pytest.raises(ValueError):
        _ = compute_hydrostatic(inp_data, water_level=1.0)

def test_override_true():
    inp_data = pl.DataFrame({
        COL_DEPTH: [0.0, 0.5, 1.0],
        COL_U0: [0.0, 5.0, 10.0]
    })

    out_data = compute_hydrostatic(inp_data, water_level=0.5, override=True)

    result = out_data[COL_U0].to_list()
    expected = [.0, .0, 4.905]

    assert result == expected

