import hashlib
from io import BytesIO
from typing import Iterable, cast

import polars as pl


def get_missing_columns(
        data: pl.DataFrame,
        required_columns: Iterable[str]
    ) -> set:

    return set(required_columns).difference(data.columns)

def dataframe_fingerprint(data: pl.DataFrame):
    data_to_bytes = cast(BytesIO, data.write_ipc(file=None)).getvalue()
    
    hash_text = hashlib.sha256(data_to_bytes).hexdigest()

    return hash_text[:16]

