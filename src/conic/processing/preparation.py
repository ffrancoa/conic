from typing import Literal, Optional

import polars as pl

from polars.exceptions import ColumnNotFoundError

from conic._canonical import (
    COL_DEPTH,
    COL_FS,
    COL_QC,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    GAMMA_WATER,
)
from conic.processing._helpers import get_column_names


def compute_hydrostatic(
    data: pl.LazyFrame,
    water_level: Optional[float] = None,
    *,
    gamma_water: float = GAMMA_WATER,
    col_depth: str = COL_DEPTH,
    col_u0: str = COL_U0,
    override: bool = False,
) -> pl.LazyFrame:

    columns = get_column_names(data)

    if col_depth not in columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )

    if col_u0 in columns and not override:
        raise ValueError(
            f"Hydrostatic pressure ({col_u0}) was already included in "
            f"this DataFrame. Set `override=True` to override."
        )

    if water_level is None:
        data_with_u0 = data.with_columns(pl.lit(0.0).alias(col_u0))
    else:
        data_with_u0 = data.with_columns(
            pl.when(pl.col(col_depth) >= water_level)
            .then((pl.col(col_depth) - water_level) * gamma_water)
            .otherwise(0.0)
            .alias(col_u0)
        )

    return data_with_u0


def compute_geostatic(
    data: pl.LazyFrame,
    gamma_soil: Optional[float] = None,
    *,
    col_depth: str = COL_DEPTH,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    col_u0: str = COL_U0,
    override: bool = False,
) -> pl.LazyFrame:

    columns = get_column_names(data)

    if col_depth not in columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )

    if {col_sv_eff, col_sv_tot}.issubset(columns) and not override:
        raise ValueError(
            f"Geostatic columns ('{col_sv_eff}' and '{col_sv_tot}') were "
            f"already included in this DataFrame. Set `override=True` to "
            f"override."
        )
    elif col_sv_tot in columns and col_sv_eff not in columns and not override:
        data_with_sv_eff = data.with_columns(
            (pl.col(col_sv_tot) - pl.col(col_u0)).alias(col_sv_eff)
        )
        return data_with_sv_eff
    elif col_sv_eff in columns and col_sv_tot not in columns and not override:
        data_with_sv_tot = data.with_columns(
            (pl.col(col_sv_eff) + pl.col(col_u0)).alias(col_sv_tot)
        )
        return data_with_sv_tot
    else:
        if gamma_soil is None or gamma_soil <= 0:
            raise ValueError(
                "A valid soil unit weight value (`gamma_soil`) must be "
                "provided to compute geostatic stresses."
            )
        return data.with_columns(
            (sv_tot_expr := pl.col(col_depth) * gamma_soil).alias(col_sv_tot),
            (sv_tot_expr - pl.col(col_u0)).alias(col_sv_eff),
        )


def adjust_depth_spacing(
    data: pl.LazyFrame,
    *,
    start_depth: Optional[float] = None,
    spacing: Optional[float] = None,
    digits: int = 3,
    col_depth: str = COL_DEPTH,
) -> pl.LazyFrame:

    if col_depth not in get_column_names(data):
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )

    start_depth_expr = (
        pl.lit(start_depth) if start_depth is not None else pl.col(col_depth).first()
    )

    spacing_expr = (
        pl.lit(spacing)
        if spacing is not None
        else pl.col(col_depth).diff().mean().round(digits)
    )

    return data.with_columns(
        (start_depth_expr + pl.int_range(pl.len()) * spacing_expr)
        .round(digits)
        .alias(col_depth)
    )


def sanitize_data(
    data: pl.LazyFrame,
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

    columns = get_column_names(data)

    if missing_columns := set(required_columns).difference(columns):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    selected_columns = required_columns

    if include_optional:
        additional_columns = set(optional_columns).intersection(columns)
        selected_columns += list(additional_columns)

    return data.select(selected_columns)


def filter_by_indicators(
    data: pl.LazyFrame,
    indicators: list[float],
    *,
    action: Literal["remove", "select"] = "remove",
) -> pl.LazyFrame:

    if action not in ["remove", "select"]:
        raise ValueError("Invalid `action` argument. Must be 'remove' or 'select'.")

    expr = pl.selectors.numeric().is_in(indicators)
    expr = pl.any_horizontal(expr)

    return data.filter(expr.not_() if action == "remove" else expr)


def split_by_indicators(
    data: pl.LazyFrame,
    indicators: list[float],
    *,
    index_col: str = "_id_",
) -> tuple[pl.LazyFrame, pl.LazyFrame]:

    indexed_data = data.with_row_index(index_col)

    rows_with = filter_by_indicators(indexed_data, indicators, action="select")
    rows_without = filter_by_indicators(indexed_data, indicators)

    return rows_with, rows_without


def clean_by_indicators(
    data: pl.LazyFrame,
    indicators: list[float],
    *,
    mode: Literal["remove", "replace"] = "replace",
) -> pl.LazyFrame:

    if mode not in ["remove", "replace"]:
        raise ValueError("Invalid `action` argument. Must be 'remove' or 'replace'.")

    match mode:
        case "remove":
            return filter_by_indicators(data, indicators, action="remove")
        case "replace":
            return data.with_columns(
                pl.when(pl.selectors.numeric().is_in(indicators))
                .then(float("nan"))
                .otherwise(pl.selectors.numeric())
                .name.keep()
            )
