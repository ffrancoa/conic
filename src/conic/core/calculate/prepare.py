import polars as pl
from polars.exceptions import ColumnNotFoundError

from conic.core._utils import get_column_names, get_missing_columns
from conic.engine._canonical import (
    CLEAN_MODE,
    COL_DEPTH,
    COL_FS,
    COL_QC,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    GAMMA_WATER,
    MAX_SLEEVE_OFFSET,
)


def _expr_estimate_mean_spacing(col_depth: str = COL_DEPTH, digits: int = 3) -> pl.Expr:
    return (
        (pl.col(col_depth).last() - pl.col(col_depth).first()) / (pl.len() - 1)
    ).round(digits)


def _expr_estimate_sleeve_offset(
    col_qc: str, col_fs: str, max_sleeve_offset: int, indicators: list[float] | None
) -> pl.Expr:

    cleaned_qc_column = pl.col(col_qc).fill_nan(None)
    cleaned_fs_column = pl.col(col_fs).fill_nan(None)

    if indicators:
        cleaned_qc_column = _expr_replace_indicators(
            cleaned_qc_column, indicators, None
        )
        cleaned_fs_column = _expr_replace_indicators(
            cleaned_fs_column, indicators, None
        )

    window_size = 2 * max_sleeve_offset + 1

    detrended_qc_column = cleaned_qc_column - cleaned_qc_column.rolling_mean(
        window_size, center=True
    )
    detrended_fs_column = cleaned_fs_column - cleaned_fs_column.rolling_mean(
        window_size, center=True
    )

    pearson_correlations = pl.concat_list(
        [
            pl.corr(detrended_qc_column, detrended_fs_column.shift(lag))
            for lag in range(-max_sleeve_offset, max_sleeve_offset + 1)
        ]
    )

    max_correlation = pearson_correlations.list.max()
    max_correlation_index = pearson_correlations.list.arg_max().cast(pl.Int64)

    return (
        pl.when(max_correlation.is_nan() | max_correlation.is_null())
        .then(pl.lit(0, dtype=pl.Int64))  # no correlation (i.e., offset = 0)
        .otherwise(max_correlation_index - max_sleeve_offset)
    )


def _expr_replace_indicators(
    target_columns: pl.Expr,
    indicators: list[float],
    value: float | None,
) -> pl.Expr:

    return (
        pl.when(target_columns.is_in(indicators)).then(value).otherwise(target_columns)
    )


def _remove_rows_with_indicators(
    lazy: pl.LazyFrame, target_columns: pl.Expr, indicators: list[float]
) -> pl.LazyFrame:

    mask = target_columns.is_in(indicators)
    global_mask = pl.any_horizontal(mask).not_()

    return lazy.filter(global_mask)


def adjust_depth_spacing(
    lazy: pl.LazyFrame,
    *,
    start_depth: float | None = None,
    spacing: float | None = None,
    digits: int = 3,
    col_depth: str = COL_DEPTH,
) -> pl.LazyFrame:

    if col_depth not in get_column_names(lazy):
        raise ColumnNotFoundError(
            f"depth column is missing in DataFrame: '{col_depth}'"
        )

    start_depth_expr = (
        pl.lit(start_depth) if start_depth is not None else pl.col(col_depth).first()
    )

    spacing_expr = (
        pl.lit(spacing)
        if spacing is not None
        else _expr_estimate_mean_spacing(col_depth, digits)
    )

    return lazy.with_columns(
        (start_depth_expr + pl.int_range(pl.len()) * spacing_expr)
        .round(digits)
        .alias(col_depth)
    )


def align_sounding(
    lazy: pl.LazyFrame,
    *,
    col_depth: str = COL_DEPTH,
    col_qc: str = COL_QC,
    col_fs: str = COL_FS,
    max_sleeve_offset: int = MAX_SLEEVE_OFFSET,
    indicators: list[float] | None = None,
) -> pl.LazyFrame:

    if missing_columns := get_missing_columns(lazy, {col_depth, col_qc, col_fs}):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'")

    if max_sleeve_offset <= 0:
        raise ValueError(
            f"maximum sleeve offset must be a positive integer; got "
            f"{max_sleeve_offset!r}"
        )

    sleeve_offset = _expr_estimate_sleeve_offset(
        col_qc, col_fs, max_sleeve_offset, indicators
    )

    return lazy.with_columns(pl.col(col_fs).shift(sleeve_offset.first()))


def clean_by_indicators(
    lazy: pl.LazyFrame,
    indicators: list[float] | None,
    *,
    mode: str = CLEAN_MODE,
    replace_value: float = float("nan"),
) -> pl.LazyFrame:

    if indicators:
        target_columns = pl.selectors.numeric()

        match mode:
            case "replace":
                return lazy.with_columns(
                    _expr_replace_indicators(
                        target_columns, indicators, replace_value
                    ).name.keep()
                )
            case "remove":
                return _remove_rows_with_indicators(lazy, target_columns, indicators)
            case _:
                raise ValueError(
                    "invalid `action` argument; use only 'replace' or 'remove'"
                )
    else:
        return lazy


def compute_hydrostatic_column(
    lazy: pl.LazyFrame,
    water_level: float | None = None,
    *,
    gamma_water: float = GAMMA_WATER,
    col_depth: str = COL_DEPTH,
    col_u0: str = COL_U0,
    override: bool = False,
) -> pl.LazyFrame:

    columns = get_column_names(lazy)

    if col_depth not in columns:
        raise ColumnNotFoundError(
            f"depth column is missing in DataFrame: '{col_depth}'"
        )

    if col_u0 in columns and not override:
        raise ValueError(
            f"hydrostatic pressure ('{col_u0}') was already included in "
            f"this DataFrame; set `override=True` to override"
        )

    if water_level is None:
        data_with_u0 = lazy.with_columns(pl.lit(0.0).alias(col_u0))
    else:
        data_with_u0 = lazy.with_columns(
            pl.when(pl.col(col_depth) >= water_level)
            .then((pl.col(col_depth) - water_level) * gamma_water)
            .otherwise(0.0)
            .alias(col_u0)
        )

    return data_with_u0


def compute_geostatic_columns(
    lazy: pl.LazyFrame,
    gamma_soil: float | None = None,
    *,
    col_depth: str = COL_DEPTH,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    col_u0: str = COL_U0,
    override: bool = False,
) -> pl.LazyFrame:

    columns = get_column_names(lazy)

    if col_depth not in columns:
        raise ColumnNotFoundError(
            f"depth column is missing in DataFrame: '{col_depth}'"
        )

    if {col_sv_eff, col_sv_tot}.issubset(columns) and not override:
        raise ValueError(
            f"geostatic columns ('{col_sv_eff}' and '{col_sv_tot}') were "
            f"already included in this DataFrame; set `override=True` to "
            f"override"
        )
    elif col_sv_tot in columns and col_sv_eff not in columns and not override:
        data_with_sv_eff = lazy.with_columns(
            (pl.col(col_sv_tot) - pl.col(col_u0)).alias(col_sv_eff)
        )
        return data_with_sv_eff
    elif col_sv_eff in columns and col_sv_tot not in columns and not override:
        data_with_sv_tot = lazy.with_columns(
            (pl.col(col_sv_eff) + pl.col(col_u0)).alias(col_sv_tot)
        )
        return data_with_sv_tot
    else:
        if gamma_soil is None or gamma_soil <= 0:
            raise ValueError(
                "a valid soil unit weight value (`gamma_soil`) must be "
                "provided to compute geostatic stresses"
            )
        return lazy.with_columns(
            (sv_tot_expr := pl.col(col_depth) * gamma_soil).alias(col_sv_tot),
            (sv_tot_expr - pl.col(col_u0)).alias(col_sv_eff),
        )


def sanitize_sounding(
    lazy: pl.LazyFrame,
    *,
    col_depth: str = COL_DEPTH,
    col_qc: str = COL_QC,
    col_fs: str = COL_FS,
    col_u2: str = COL_U2,
    col_u0: str = COL_U0,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    include_optional: bool = True,
) -> pl.LazyFrame:

    required_columns = [col_depth, col_qc, col_fs, col_u2]
    optional_columns = [col_u0, col_sv_eff, col_sv_tot]

    columns = get_column_names(lazy)

    if missing_columns := set(required_columns).difference(columns):
        raise ColumnNotFoundError(f"missing required columns: '{missing_columns}'.")

    selected_columns = required_columns

    if include_optional:
        additional_columns = set(optional_columns).intersection(columns)
        selected_columns += list(additional_columns)

    return lazy.select(selected_columns)
