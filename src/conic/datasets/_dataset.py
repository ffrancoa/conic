from dataclasses import dataclass
from typing import cast

import polars as pl

from conic.datasets._registry import DatasetEntry


@dataclass(frozen=True, slots=True)
class ConicDataset:
    meta: DatasetEntry
    data: pl.LazyFrame

    def __len__(self) -> int:
        return self.meta.n_soundings

    def get_sounding(self, sounding_id: int) -> pl.DataFrame:
        if not 1 <= sounding_id <= self.meta.n_soundings:
            raise ValueError(
                f"sounding id must be in 1..{self.meta.n_soundings}; got {sounding_id}"
            )

        return cast(
            pl.DataFrame,
            self.data.filter(pl.col(self.meta.source.id_col) == sounding_id)
            .select(self.meta.columns)
            .collect(),
        )
