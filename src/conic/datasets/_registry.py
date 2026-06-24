import re
from dataclasses import dataclass

from conic.datasets._metadata import PREMSTALLER, TAILINGS, SourceMetadata
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


def _get_zenodo_url(zenodo_record: str, filename: str) -> str:
    return f"https://zenodo.org/records/{zenodo_record}/files/{filename}?download=1"


@dataclass(frozen=True, slots=True)
class DatasetEntry:
    name: str
    filename: str
    sha256: str
    test_type: str
    n_soundings: int
    columns: tuple[str, ...]
    source: SourceMetadata

    @property
    def url(self) -> str:
        return _get_zenodo_url(self.source.record, self.filename)


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
        sha256="7e7f25d5433dac56d2019b33ce743077868ad796211a249b8a8d6ea1140bb15a",
        test_type="CPTu",
        n_soundings=312,
        columns=_CPTU_COLUMNS,
        source=PREMSTALLER,
    ),
    DatasetEntry(
        name="premstaller_scptu",
        filename="premstaller_scptu.parquet",
        sha256="0a4775a24c49d5d5ca5898796355111d10106bb7a8b6b5e23b73c782c32f8128",
        test_type="SCPTu",
        n_soundings=50,
        columns=_SCPTU_COLUMNS,
        source=PREMSTALLER,
    ),
    DatasetEntry(
        name="tailings_cptu",
        filename="tailings_cptu.parquet",
        sha256="ddfec64ca05ba95d65e55ef86538018267d89e0fb02685155029c42811bc8e22",
        test_type="CPTu",
        n_soundings=16,
        columns=_CPTU_COLUMNS,
        source=TAILINGS,
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


def _get_entries(source: str) -> tuple[DatasetEntry, ...]:
    prefix = f"{source.lower()}_"
    entries = tuple(entry for entry in ENTRIES if entry.name.startswith(prefix))

    if not entries:
        available = ", ".join(sorted(_BY_NAME))
        raise ValueError(
            f"unknown dataset source {source!r}; available datasets are: '{available}'"
        )

    return entries


def _title_from_citation(citation: str) -> str:
    match = re.search(r"\(\d{4}\)\.\s*(.*?)\.", citation)
    return match.group(1) if match else citation


def list_datasets(name: str | None = None) -> None:
    if name is None:
        sources = tuple(
            dict.fromkeys(entry.name.rsplit("_", 1)[0] for entry in ENTRIES)
        )
    else:
        sources = (name,)

    for source in sources:
        entries = _get_entries(source)
        meta = entries[0]

        title = _title_from_citation(meta.source.citation)
        variants = " · ".join(f"{e.test_type} ({e.n_soundings})" for e in entries)

        print(f"\n▌ {title} [{source!r}]")
        print(f"    Reference : {meta.source.reference}")
        print(f"    Soundings : {variants}")
        print(f"    DOI       : {meta.source.doi}")
        print(f"    License   : {meta.source.license}")
