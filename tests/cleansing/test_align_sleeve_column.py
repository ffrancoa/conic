import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.engine._defaults import COL_DEPTH, COL_FS, COL_QC
from conic.processing._cleansing import align_sleeve_column

# Signal with clear transitions for lag estimation.
_BLOCK = [0.0] * 5 + [10.0] * 5


def _make_lazy(qc: list[float], fs: list[float]) -> pl.LazyFrame:
    return pl.DataFrame(
        {
            COL_DEPTH: [i * 0.02 for i in range(len(qc))],
            COL_QC: qc,
            COL_FS: fs,
        }
    ).lazy()


def _lagged(signal: list[float], k: int) -> list[float]:
    """fs lags qc by k rows: fs[i] = qc[i - k]."""
    return [0.0] * k + signal[:-k]


def _align(lazy: pl.LazyFrame, *, max_sleeve_offset: int, **kwargs) -> pl.LazyFrame:
    return align_sleeve_column(
        lazy, COL_DEPTH, COL_QC, COL_FS, max_sleeve_offset=max_sleeve_offset, **kwargs
    )


# --- error cases ---


def test_missing_columns_raises():
    data = pl.DataFrame({COL_DEPTH: [0.0, 0.5]}).lazy()
    with pytest.raises(ColumnNotFoundError):
        _align(data, max_sleeve_offset=3).collect()


def test_invalid_max_sleeve_offset_raises():
    data = _make_lazy([0.0, 1.0], [0.0, 1.0])
    with pytest.raises(ValueError, match="positive integer"):
        _align(data, max_sleeve_offset=0).collect()


def test_negative_max_sleeve_offset_raises():
    data = _make_lazy([0.0, 1.0], [0.0, 1.0])
    with pytest.raises(ValueError):
        _align(data, max_sleeve_offset=-1).collect()


# --- zero offset (identity) ---


def test_zero_offset_preserves_length_and_values():
    signal = (_BLOCK * 4)[:30]
    lazy = _make_lazy(signal, signal)
    result = _align(lazy, max_sleeve_offset=3).collect()

    assert len(result) == len(signal)
    assert result[COL_FS].to_list() == signal


# --- positive offset ---


def test_k2_preserves_all_rows():
    k = 2
    qc_vals = _BLOCK * 4
    fs_vals = _lagged(qc_vals, k)
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=5).collect()

    assert len(result) == len(qc_vals)


def test_k2_aligns_fs_with_null_tail():
    k = 2
    qc_vals = _BLOCK * 4
    fs_vals = _lagged(qc_vals, k)
    n = len(qc_vals)
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=5).collect()

    assert result[COL_FS][: n - k].to_list() == qc_vals[: n - k]
    assert result[COL_FS][-k:].is_null().all()


def test_k3_preserves_all_rows():
    k = 3
    qc_vals = _BLOCK * 5
    fs_vals = _lagged(qc_vals, k)
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=5).collect()

    assert len(result) == len(qc_vals)


def test_k3_aligns_fs_with_null_tail():
    k = 3
    qc_vals = _BLOCK * 5
    fs_vals = _lagged(qc_vals, k)
    n = len(qc_vals)
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=5).collect()

    assert result[COL_FS][: n - k].to_list() == qc_vals[: n - k]
    assert result[COL_FS][-k:].is_null().all()


# --- degenerate / flat signal ---


def test_flat_signal_preserves_length():
    vals = [5.0] * 30
    lazy = _make_lazy(vals, vals)
    result = _align(lazy, max_sleeve_offset=3).collect()

    assert len(result) == 30


def test_flat_signal_preserves_fs_values():
    vals = [5.0] * 30
    lazy = _make_lazy(vals, vals)
    result = _align(lazy, max_sleeve_offset=3).collect()

    assert result[COL_FS].to_list() == vals


# --- indicators ---


def test_indicators_accepted_without_error():
    k = 2
    sentinel = -999.0
    qc_vals = _BLOCK * 4
    fs_vals = _lagged(qc_vals, k)
    n = len(qc_vals)
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=5, indicators=[sentinel]).collect()

    assert len(result) == n


def test_indicators_sentinel_columns_excluded():
    sentinel = -9999.0
    n = 30
    qc_vals = [sentinel] * n
    fs_vals = [5.0] * n
    lazy = _make_lazy(qc_vals, fs_vals)

    result = _align(lazy, max_sleeve_offset=3, indicators=[sentinel]).collect()

    assert len(result) == n
    assert result[COL_FS].to_list() == fs_vals
