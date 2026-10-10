import polars as pl
from polars.testing import assert_frame_equal

from conic import catalog
from conic.express import process_standard
from conic.workflow import Configurator, Pipeliner
from conic.workflow._defaults import COL_DEPTH, COL_FS, COL_QC, COL_U2


def test_process_standard_with_extras():
    config = Configurator.from_dict({"parameters": {"gamma_soil": 20.0}})
    extras = (catalog.add_bi14_columns(), catalog.add_rw98_columns())

    inp_data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    returned = process_standard(inp_data, config, extras=extras)
    expected = Pipeliner.standard(config, extras=extras).run(inp_data)

    assert_frame_equal(returned, expected)
