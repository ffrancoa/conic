import hashlib
from io import BytesIO
from typing import cast

import polars as pl

from conic.config import Processor


def get_fingerprint(data: pl.DataFrame):
    data_to_bytes = cast(BytesIO, data.write_ipc(file=None)).getvalue()
    
    hash_text = hashlib.sha256(data_to_bytes).hexdigest()

    return hash_text[:16]

def validate_columns(data: pl.DataFrame, processor: Processor) -> None:
    config_columns = processor.columns.input
    
    required_columns = (
        config_columns.depth,
        config_columns.qc,
        config_columns.fs,
        config_columns.u2
    )

    data_columns = data.columns

    missing_columns = set(required_columns).difference(data_columns)

    if missing_columns:
        raise ValueError(
            f"DataFrame is missing required columns: {missing_columns}."
        )

