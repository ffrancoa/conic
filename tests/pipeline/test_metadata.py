import polars as pl

from conic.config import Parameters, Processor
from conic.pipeline import Pipeliner
from conic._canonical import COL_DEPTH, COL_QC


def test_metadata_unpacking():
    processor = Processor(parameters=Parameters(water_level=2.0))
    pipeliner = Pipeliner.default(processor)

    inp_data = pl.DataFrame({
        COL_DEPTH: [0.0, 1.0, 2.0, 3.0],
        COL_QC: [1.1, 0.9, 1.5, 1.4]
    })

    out_data, meta = pipeliner.run(inp_data, metadata=True, validate=False)

    assert isinstance(out_data, pl.DataFrame)
    assert isinstance(meta, dict)

def test_metadata_fields():
    processor = Processor(parameters=Parameters(water_level=2.0))
    pipeliner = Pipeliner.default(processor)

    data = pl.DataFrame({
        COL_DEPTH: [0.0, 1.0, 2.0, 3.0],
        COL_QC: [1.1, 0.9, 1.5, 1.4]
    })

    result = pipeliner.run(data, metadata=True, validate=False)

    assert set(result.metadata.keys()) == {
        "data_hash", "source_path", "processor", "steps", "timestamp_utc"
    }


def test_hash_is_deterministic():
    processor = Processor(parameters=Parameters(water_level=1.0))
    pipeliner = Pipeliner.default(processor)

    data = pl.DataFrame({
        COL_DEPTH: [0.0, 1.0, 2.0, 3.0],
        COL_QC: [1.1, 0.9, 1.5, 1.4]
    })

    _, meta1 = pipeliner.run(data, metadata=True, validate=False)
    _, meta2 = pipeliner.run(data, metadata=True, validate=False)
    
    assert meta1["data_hash"] == meta2["data_hash"]

