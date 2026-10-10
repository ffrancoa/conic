import tomllib
from dataclasses import dataclass
from pathlib import Path

from conic.workflow._defaults import (
    COL_DEPTH,
    COL_FS,
    COL_QC,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    COL_VS,
)

_REGISTRY_PATH = Path(__file__).parent / "registry.toml"
_ID_COL: str = "Sorted ID"

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

_TEST_TYPES: dict[str, tuple[str, tuple[str, ...]]] = {
    "cptu": ("CPTu", _CPTU_COLUMNS),
    "scptu": ("SCPTu", _SCPTU_COLUMNS),
}


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    citation: str
    doi: str
    license: str
    record: str
    reference: str


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
        return (
            f"https://zenodo.org/records/{self.source.record}"
            f"/files/{self.filename}?download=1"
        )


def _load_registry() -> tuple[DatasetEntry, ...]:
    with _REGISTRY_PATH.open("rb") as f:
        raw = tomllib.load(f)

    entries: list[DatasetEntry] = []

    for source_name, source_data in raw["sources"].items():
        meta = SourceMetadata(
            citation=source_data["citation"],
            doi=source_data["doi"],
            license=source_data["license"],
            record=source_data["record"],
            reference=source_data["reference"],
        )

        for entry_key, entry_data in source_data["entries"].items():
            test_label, columns = _TEST_TYPES[entry_key]
            entries.append(
                DatasetEntry(
                    name=f"{source_name}_{entry_key}",
                    filename=entry_data["filename"],
                    sha256=entry_data["sha256"],
                    test_type=test_label,
                    n_soundings=entry_data["n_soundings"],
                    columns=columns,
                    source=meta,
                )
            )

    return tuple(entries)


_ENTRIES: tuple[DatasetEntry, ...] = _load_registry()
_BY_NAME: dict[str, DatasetEntry] = {entry.name: entry for entry in _ENTRIES}


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
    entries = tuple(entry for entry in _ENTRIES if entry.name.startswith(prefix))

    if not entries:
        available = ", ".join(sorted(_BY_NAME))
        raise ValueError(
            f"unknown dataset source {source!r}; available datasets are: '{available}'"
        )

    return entries
