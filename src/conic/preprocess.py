from typing import cast, Literal, Optional

import polars as pl
from polars.exceptions import ColumnNotFoundError
from pydantic import NonNegativeFloat, PositiveFloat

from ._canonical import COL_DEPTH, COL_U0, GAMMA_WATER
from .config import ColumnName, CleanMode


type FilterAction = Literal["remove", "select"]


def compute_hydrostatic(
        data: pl.DataFrame, *,
        water_level: NonNegativeFloat,
        gamma_water: PositiveFloat = GAMMA_WATER,
        col_depth: ColumnName = COL_DEPTH,
        col_u0: ColumnName = COL_U0,
        override: bool = False
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

    data_with_u0 = data.with_columns(
        pl.when(pl.col(col_depth) >= water_level)
        .then((pl.col(col_depth) - water_level) * gamma_water)
        .otherwise(0.0)
        .alias(col_u0)
    )

    return data_with_u0

def adjust_depth_spacing(
        data: pl.DataFrame, *,
        start_depth: Optional[NonNegativeFloat] = None,
        spacing: Optional[PositiveFloat] = None,
        round_digits: int = 3,
        col_depth: ColumnName = COL_DEPTH,
    ) -> pl.DataFrame:

    if col_depth not in data.columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )
        
    if start_depth is None and spacing is None:
        raise ValueError(
            "Both `start_depth` and `spacing` cannot be set to "
            "`None`. Please, set at least one of those parameters."
        ) 

    if (nrows := data.height) < 2:
        raise ValueError(
            "DataFrame must have at least 2 rows to infer depth spacing. "
        )

    if start_depth is None:
        start_depth = data.item(0, col_depth)

    if spacing is None:
        mean_spacing = data.get_column(col_depth).diff().mean()
        spacing = cast(float, mean_spacing)

    new_depths = start_depth + pl.int_range(nrows, eager=True) * spacing
    new_depths = new_depths.round(round_digits)

    return data.with_columns(new_depths.alias(col_depth))

def filter_by_indicators(
        data: pl.DataFrame,
        indicators: list[float], *,
        action: FilterAction = "remove"
    ) -> pl.DataFrame:

    if action not in ["remove", "select"]:
        raise ValueError(
            "Invalid `action` argument. Must be 'remove' or 'select'."
        )

    expr = pl.selectors.numeric().is_in(indicators)
    expr = pl.any_horizontal(expr)
    
    return data.filter(expr.not_() if action == "remove" else expr)

def split_by_indicators(
        data: pl.DataFrame,
        indicators: list[float], *,
        index_col: str = "_id_"        
    ) -> tuple[pl.DataFrame, pl.DataFrame]:

    indexed_data = data.with_row_index(index_col)

    rows_with = filter_by_indicators(indexed_data, indicators, action="select")
    rows_without = filter_by_indicators(indexed_data, indicators)
    
    return rows_with, rows_without

def clean_by_indicators(
        data: pl.DataFrame,
        indicators: list[float], *,
        mode: CleanMode = "replace"
    ) -> pl.DataFrame:

    if mode not in ["remove", "replace"]:
        raise ValueError(
            "Invalid `action` argument. Must be 'remove' or 'replace'."
        )

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

