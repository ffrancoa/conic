from dataclasses import dataclass

from conic.datasets._metadata import (
    PREMSTALLER_CITATION,
    PREMSTALLER_DOI,
    PREMSTALLER_ID_COL,
    PREMSTALLER_LICENSE,
    PREMSTALLER_RECORD,
)
from conic.engine._canonical import (
    COL_DEPTH,
    COL_FS,
    COL_QC,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    COL_VS,
)


@dataclass(frozen=True, slots=True)
class DatasetEntry:
    name: str
    filename: str
    url: str
    sha256: str
    test_type: str
    n_soundings: int
    columns: tuple[str, ...]
    id_column: str
    citation: str
    doi: str
    license: str


def _get_zenodo_url(zenodo_record: str, filename: str) -> str:
    return f"https://zenodo.org/records/{zenodo_record}/files/{filename}?download=1"


_CPTU_COLUMNS: tuple[str, ...] = (
    COL_DEPTH,
    COL_QC,
    COL_FS,
    COL_U2,
    COL_U0,
    COL_SV_TOT,
    COL_SV_EFF,
)

_SCPTU_COLUMNS: tuple[str, ...] = (*_CPTU_COLUMNS, COL_VS)


ENTRIES: tuple[DatasetEntry, ...] = (
    DatasetEntry(
        name="premstaller_cptu",
        filename="premstaller_cptu.parquet",
        url=_get_zenodo_url(PREMSTALLER_RECORD, "premstaller_cptu.parquet"),
        sha256="5ede5e284139fe382b0d47ff9842d49a676149b4a31332304bc9351d0a8c4d55",
        test_type="CPTu",
        n_soundings=312,
        columns=_CPTU_COLUMNS,
        id_column=PREMSTALLER_ID_COL,
        citation=PREMSTALLER_CITATION,
        doi=PREMSTALLER_DOI,
        license=PREMSTALLER_LICENSE,
    ),
    DatasetEntry(
        name="premstaller_scptu",
        filename="premstaller_scptu.parquet",
        url=_get_zenodo_url(PREMSTALLER_RECORD, "premstaller_scptu.parquet"),
        sha256="4275f38f363e0aa516c933ca8d0ff315a9f81618a19785c66b0f0375f2845cfa",
        test_type="SCPTu",
        n_soundings=50,
        columns=_SCPTU_COLUMNS,
        id_column=PREMSTALLER_ID_COL,
        citation=PREMSTALLER_CITATION,
        doi=PREMSTALLER_DOI,
        license=PREMSTALLER_LICENSE,
    ),
)


_BY_NAME: dict[str, DatasetEntry] = {entry.name: entry for entry in ENTRIES}


def _get_entry(name: str) -> DatasetEntry:
    try:
        return _BY_NAME[name]
    except KeyError:
        available = ", ".join(sorted(_BY_NAME))
        raise ValueError(
            f"unknown dataset {name!r}; available datasets are: '{available}'"
        ) from None


def list_datasets(*, test_type: str | None = None) -> tuple[DatasetEntry, ...]:
    return tuple(
        entry
        for entry in ENTRIES
        if (test_type is None or entry.test_type == test_type)
    )
