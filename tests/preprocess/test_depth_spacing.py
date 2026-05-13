import polars as pl
import pytest

from conic import preprocess

def test_signature():
    data = pl.DataFrame({
            "Depth (m)": [0.0, 0.5, 1.5, 2.0]
        })
    with pytest.raises(NotImplementedError):
        preprocess.adjust_depth_spacing(data)        

