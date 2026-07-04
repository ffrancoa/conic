import hashlib
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import platformdirs
import polars as pl

from conic.datasets._dataset import ConicDataset
from conic.datasets._registry import DatasetEntry, _get_entries, _get_entry

_TIMEOUT: float = 30.0

_CHUNK: int = 1 << 20

_USER_AGENT: str = "conic"


def _datasets_root(cache_path: Path | str | None = None) -> Path:
    if cache_path is not None:
        return Path(cache_path)

    override = os.environ.get("CONIC_DATA")

    if override:
        return Path(override)

    return Path(platformdirs.user_cache_dir("conic")) / "datasets"


def _get_entry_path(entry: DatasetEntry, cache_path: Path | str | None = None) -> Path:
    return _datasets_root(cache_path) / entry.sha256 / entry.filename


def _download_entry(entry: DatasetEntry, dest_path: Path) -> str:
    if urlsplit(entry.url).scheme != "https":
        raise ValueError(f"refusing non-https dataset url: {entry.url!r}")

    digest = hashlib.sha256()
    request = urllib.request.Request(entry.url, headers={"User-Agent": _USER_AGENT})

    try:
        with (
            urllib.request.urlopen(request, timeout=_TIMEOUT) as response,
            dest_path.open("wb") as dataset_file,
        ):
            while chunk := response.read(_CHUNK):
                dataset_file.write(chunk)
                digest.update(chunk)
    except (urllib.error.URLError, TimeoutError) as error:
        raise ConnectionError(
            f"could not download dataset {entry.name!r} from {entry.url}: {error}"
        ) from error

    return digest.hexdigest()


def _fetch_to_cache(entry: DatasetEntry, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_file, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(tmp_file)

    tmp_path = Path(tmp_name)

    try:
        fingerprint = _download_entry(entry, tmp_path)

        if fingerprint != entry.sha256:
            raise ValueError(
                f"hash mismatch for {entry.name!r}: "
                f"expected {entry.sha256}, got {fingerprint}"
            )

        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _ensure_entry(entry: DatasetEntry, cache_path: Path | str | None = None) -> Path:
    path = _get_entry_path(entry, cache_path)

    if not path.exists():
        _fetch_to_cache(entry, path)

    return path


def fetch_dataset(
    source: str,
    test_type: str = "all",
    *,
    cache_path: Path | str | None = None,
) -> None:

    test_types = ("cptu", "scptu", "all")

    if test_type not in test_types:
        available = ", ".join(test_types)
        raise ValueError(
            f"unknown test type {test_type!r}; available test types are: '{available}'"
        )

    if test_type == "all":
        entries = _get_entries(source)
    else:
        entries = (_get_entry(f"{source.lower()}_{test_type}"),)

    for entry in entries:
        _ensure_entry(entry, cache_path)


def load_dataset(
    source: str,
    test_type: str = "cptu",
    *,
    cache_path: Path | str | None = None,
) -> ConicDataset:

    test_types = ("cptu", "scptu")

    if test_type not in test_types:
        available = ", ".join(test_types)
        raise ValueError(
            f"unknown test type {test_type!r}; available test types are: '{available}'"
        )

    entry = _get_entry(f"{source.lower()}_{test_type.lower()}")
    path = _ensure_entry(entry, cache_path)

    return ConicDataset(meta=entry, data=pl.scan_parquet(path))
