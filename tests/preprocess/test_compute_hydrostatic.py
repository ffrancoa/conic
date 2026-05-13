import polars as pl
import pytest

from conic import preprocess

def test_signature():
    data = pl.DataFrame({
            "Depth (m)": [0.0]
        })
    with pytest.raises(NotImplementedError):
        preprocess.compute_hydrostatic(data, water_level=3.0)        

