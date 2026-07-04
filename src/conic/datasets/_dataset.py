from dataclasses import dataclass

import polars as pl

from conic.datasets._registry import _ID_COL, DatasetEntry


@dataclass(frozen=True, slots=True)
class ConicDataset:
    meta: DatasetEntry
    data: pl.LazyFrame

    def __len__(self) -> int:
        return self.meta.n_soundings

    def get_sounding(self, sounding_id: int) -> pl.DataFrame:
        if not 1 <= sounding_id <= self.meta.n_soundings:
            raise ValueError(
                f"`sounding id` must be in range 1..{self.meta.n_soundings}; got "
                f"{sounding_id!r}"
            )

        return (
            self.data.filter(pl.col(_ID_COL) == sounding_id)
            .select(self.meta.columns)
            .collect()
        )
