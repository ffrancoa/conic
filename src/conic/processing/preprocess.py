from typing import Literal, Optional, cast

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
from conic.processing._helpers import get_missing_columns


def compute_hydrostatic(
    data: pl.DataFrame,
    water_level: Optional[float] = None,
    *,
    gamma_water: float = GAMMA_WATER,
    col_depth: str = COL_DEPTH,
    col_u0: str = COL_U0,
    override: bool = False,
) -> pl.DataFrame:

    if col_depth not in data.columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )

    if col_u0 in data.columns and not override:
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


def adjust_depth_spacing(
    data: pl.DataFrame,
    *,
    start_depth: Optional[float] = None,
    spacing: Optional[float] = None,
    digits: int = 3,
    col_depth: str = COL_DEPTH,
) -> pl.DataFrame:

    if col_depth not in data.columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )

    if (nrows := data.height) < 2:
        raise ValueError("DataFrame must have at least 2 rows to infer depth spacing. ")

    if start_depth is None:
        start_depth = data.item(0, col_depth)

    if spacing is None:
        mean_spacing = data.get_column(col_depth).diff().mean()
        spacing = round(cast(float, mean_spacing), digits)

    new_depths = start_depth + pl.int_range(nrows, eager=True) * spacing
    new_depths = new_depths.round(digits)

    return data.with_columns(new_depths.alias(col_depth))


def sanitize_data(
    data: pl.DataFrame,
    *,
    col_depth: str = COL_DEPTH,
    col_qc: str = COL_QC,
    col_fs: str = COL_FS,
    col_u2: str = COL_U2,
    col_u0: str = COL_U0,
    col_sv_eff: str = COL_SV_EFF,
    col_sv_tot: str = COL_SV_TOT,
    include_optional: bool = True,
) -> pl.DataFrame:

    required_columns = [col_depth, col_qc, col_fs, col_u2]
    optional_columns = [col_u0, col_sv_eff, col_sv_tot]

    if missing_columns := get_missing_columns(data, required_columns):
        raise ColumnNotFoundError(f"Missing required columns: '{missing_columns}'.")

    selected_columns = required_columns

    if include_optional:
        additional_columns = set(optional_columns).intersection(data.columns)
        selected_columns += list(additional_columns)

    return data.select(selected_columns)


def filter_by_indicators(
    data: pl.DataFrame,
    indicators: list[float],
    *,
    action: Literal["remove", "select"] = "remove",
) -> pl.DataFrame:

    if action not in ["remove", "select"]:
        raise ValueError("Invalid `action` argument. Must be 'remove' or 'select'.")

    expr = pl.selectors.numeric().is_in(indicators)
    expr = pl.any_horizontal(expr)

    return data.filter(expr.not_() if action == "remove" else expr)


def split_by_indicators(
    data: pl.DataFrame, indicators: list[float], *, index_col: str = "_id_"
) -> tuple[pl.DataFrame, pl.DataFrame]:

    indexed_data = data.with_row_index(index_col)

    rows_with = filter_by_indicators(indexed_data, indicators, action="select")
    rows_without = filter_by_indicators(indexed_data, indicators)

    return rows_with, rows_without


def clean_by_indicators(
    data: pl.DataFrame,
    indicators: list[float],
    *,
    mode: Literal["remove", "replace"] = "replace",
) -> pl.DataFrame:

    if mode not in ["remove", "replace"]:
        raise ValueError("Invalid `action` argument. Must be 'remove' or 'replace'.")

    match mode:
        case "remove":
            return filter_by_indicators(data, indicators, action="remove")
        case "replace":
            return data.with_columns(
                pl.when(pl.selectors.numeric().is_in(indicators))
                .then(None)
                .otherwise(pl.selectors.numeric())
                .name.keep()
            )
