import polars as pl

from conic.config import Configurator
from conic.config._defaults import COL_DEPTH, COL_FS, COL_QC, COL_U0, COL_U2
from conic.pipeline import Pipeliner
from conic.pipeline._core import Step, _standard_ops
from conic.tools import inverse_filter


def test_default_pipeliner():
    config = Configurator.from_dict({"parameters": {"gamma_soil": 20.0}})
    pipe = Pipeliner.standard(config)

    inp_data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    out_data = pipe.run(inp_data)

    assert COL_U0 in out_data.columns


def test_custom_pipeliner():
    config = Configurator()

    add_eight = Step(
        name="add_eight",
        apply=lambda df: df.with_columns((pl.col(COL_QC) + 8).alias(COL_QC)),
    )

    pipe = Pipeliner(config, steps=(add_eight,))

    inp_data = pl.DataFrame(
        {
            COL_DEPTH: [2.0, 2.4, 3.0, 3.4, 4.0],
            COL_QC: [0.9, 1.3, 1.5, 1.2, 1.4],
            COL_FS: [35.2, 45.1, 23.4, 53.2, 47.7],
            COL_U2: [10.5, 20.4, 14.5, 19.5, 30.6],
        }
    )

    out_data = pipe.run(inp_data)

    returned = out_data[COL_QC].to_list()
    expected = [8.9, 9.3, 9.5, 9.2, 9.4]

    assert returned == expected


def test_inverse_filter_after_sleeve_alignment():
    config = Configurator.from_dict(
        {"parameters": {"gamma_soil": 20.0}, "cleansing": {"max_sleeve_offset": 3}}
    ).with_tool("inverse_filter", inverse_filter.Config())
    pipe = Pipeliner.from_operations(
        config, (*_standard_ops(), inverse_filter.operation())
    )

    qc_vals = ([1.0] * 5 + [6.0] * 5) * 6
    fs_vals = [10.0, 10.0] + [10.0 * qc for qc in qc_vals[:-2]]

    inp_data = pl.DataFrame(
        {
            COL_DEPTH: [1.0 + 0.02 * i for i in range(len(qc_vals))],
            COL_QC: qc_vals,
            COL_FS: fs_vals,
            COL_U2: [20.0] * len(qc_vals),
        }
    )

    out_data = pipe.run(inp_data)
    columns = inverse_filter.Columns()

    assert out_data[COL_FS][-2:].is_nan().all()
    assert out_data[COL_FS].null_count() == 0
    assert out_data[columns.qt_inv].is_finite().all()
