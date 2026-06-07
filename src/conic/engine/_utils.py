import hashlib
from io import BytesIO
from typing import cast

import polars as pl


def get_dataframe_fingerprint(data: pl.DataFrame) -> str:
    hasher = hashlib.sha256()
    hasher.update(str(data.schema).encode())

    hash_frame = data.hash_rows().to_frame()
    hash_bytes = cast(BytesIO, hash_frame.write_ipc(file=None)).getvalue()

    hasher.update(hash_bytes)

    return hasher.hexdigest()[:16]
