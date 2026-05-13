from typing import Optional

import polars as pl
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

    if col_u0 in data.columns and not override:
            raise ValueError("")

    data_with_u0 = data.with_columns(
        pl.when(pl.col(col_depth) >= water_level)
        .then((pl.col(col_depth) - water_level) * gamma_water)
        .otherwise(0.0)
        .alias(col_u0)
    )

    return data_with_u0

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

def adjust_depth_spacing(
        data: pl.DataFrame, *,
        start_depth: Optional[NonNegativeFloat] = None,
        spacing: Optional[PositiveFloat] = None,
        round_digits: int = 3,
        col_depth: ColumnName = COL_DEPTH,
        override: bool = False
    ) -> pl.DataFrame:

    raise NotImplementedError

def split_data_by_ind(
        data: pl.DataFrame, *,
        indicators: list[float],
        index_col: str = "_id_"        
    ) -> tuple[pl.DataFrame, pl.DataFrame]:

    raise NotImplementedError

