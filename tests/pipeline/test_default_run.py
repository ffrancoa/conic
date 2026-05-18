import polars as pl

from conic.pipeline import Pipeliner, Step
from conic.config import Configurator
from conic._canonical import COL_DEPTH, COL_QC, COL_FS, COL_U2, COL_U0

def test_default_pipeliner():
    config = Configurator()
    pipe = Pipeliner.default(config)

    inp_data = pl.DataFrame({
        COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
        COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
        COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
        COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6]
    })
    
    out_data = pipe.run(inp_data)

    assert COL_U0 in out_data.columns

def test_custom_pipeliner():
    config = Configurator()
    
    add_eight = Step(name="add_eight", apply=lambda df: df.with_columns(
        (pl.col(COL_QC) + 8).alias(COL_QC)
    ))

    pipe = Pipeliner(config, steps=(add_eight,))

    inp_data = pl.DataFrame({
        COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
        COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
        COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
        COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6]
    })

    out_data = pipe.run(inp_data)

    returned = out_data[COL_QC].to_list()
    expected = [8.9, 9.3, 9.5, 9.2, 9.4]

    assert returned == expected
