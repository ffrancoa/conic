import polars as pl

from conic._canonical import COL_DEPTH, COL_FS, COL_QC, COL_U2
from conic.config import Configurator, Parameters
from conic.pipeline import Pipeliner


def test_metadata_unpacking():
    config = Configurator(parameters=Parameters(water_level=2.0))
    pipeliner = Pipeliner.default(config)

    inp_data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    out_data, meta = pipeliner.run(inp_data, metadata=True)

    assert isinstance(out_data, pl.DataFrame)
    assert isinstance(meta, dict)


def test_metadata_fields():
    config = Configurator(parameters=Parameters(water_level=2.0))
    pipeliner = Pipeliner.default(config)

    data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    result = pipeliner.run(data, metadata=True)

    assert set(result.metadata.keys()) == {
        "data_hash",
        "source_path",
        "config",
        "steps",
        "timestamp_utc",
    }


def test_hash_is_deterministic():
    config = Configurator(parameters=Parameters(water_level=1.0))
    pipeliner = Pipeliner.default(config)

    data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    _, meta1 = pipeliner.run(data, metadata=True)
    _, meta2 = pipeliner.run(data, metadata=True)

    assert meta1["data_hash"] == meta2["data_hash"]
