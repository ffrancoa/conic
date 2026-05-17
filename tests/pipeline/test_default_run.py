import polars as pl

from conic.pipeline import Pipeliner, Step
from conic.config import Processor
from conic._canonical import COL_DEPTH, COL_QC, COL_U0

def test_default_pipeliner():
    proc = Processor()
    pipe = Pipeliner.default(proc)

    inp_data = pl.DataFrame({
        COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
        COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4]
    })
    
    out_data = pipe.run(inp_data, validate=False)

    assert COL_U0 in out_data.columns

def test_custom_pipeliner():
    proc = Processor()
    add_eight = Step(name="add_eight", apply=lambda df: df.with_columns(
        (pl.col(COL_QC) + 8).alias(COL_QC)
    ))

    pipe = Pipeliner(proc, steps=(add_eight,))

    inp_data = pl.DataFrame({
        COL_DEPTH: [1.2, 1.4, 1.6],
        COL_QC: [0.3, 0.7, 0.8]
    })

    out_data = pipe.run(inp_data, validate=False)

    returned = out_data[COL_QC].to_list()
    expected = [8.3, 8.7, 8.8]

    assert returned == expected
