from typing import Optional, cast

import polars as pl
from polars.exceptions import ColumnNotFoundError
from pydantic import NonNegativeFloat, PositiveFloat

from ._canonical import COL_DEPTH, COL_U0, GAMMA_WATER
from .config import ColumnName


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
        override: bool = False
    ) -> pl.DataFrame:

    if col_depth not in data.columns:
        raise ColumnNotFoundError(
            f"Depth column is missing in DataFrame: '{col_depth}'."
        )
        
    if not (start_depth or spacing):
        raise ValueError(
            "Both `start_depth` and `spacing` cannot be set to "
            "`None`. Please, set at least one of those parameters."
        ) 

    if (nrows := data.height) < 2:
        raise ValueError(
            "DataFrame must have at least 2 rows to infer depth spacing. "
        )

    if not start_depth:
        start_depth = data.item(0, col_depth)

    if not spacing:
        mean_spacing = data.get_column(col_depth).diff().mean()
        spacing = cast(float, mean_spacing)

    new_depths = start_depth + pl.int_range(nrows, eager=True) * spacing
    new_depths = new_depths.round(round_digits)

    return data.with_columns(new_depths.alias(COL_DEPTH))

def remove_rows_with_ind(
        data: pl.DataFrame, *,
        indicators: list[float]
    ) -> pl.DataFrame:

    raise NotImplementedError

def replace_rows_with_ind(
        data: pl.DataFrame, *,
        indicators: list[float],
        value: Optional[float] = None
    ) -> pl.DataFrame:

    raise NotImplementedError
    
def split_data_by_ind(
        data: pl.DataFrame, *,
        indicators: list[float],
        index_col: str = "_id_"        
    ) -> tuple[pl.DataFrame, pl.DataFrame]:

    raise NotImplementedError

