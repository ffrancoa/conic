import dataclasses
from dataclasses import dataclass
from typing import Any, Self

from conic.tools.inverse_filter._defaults import (
    COL_CONVG_INV,
    COL_DEPTH,
    COL_FR,
    COL_FS,
    COL_FS_INV,
    COL_QT,
    COL_QT_INV,
    COL_SV_EFF,
    COL_SV_TOT,
)


def _validate_keys(cls, data: dict[str, Any]) -> None:
    valid_fields = {field.name for field in dataclasses.fields(cls)}
    unknown_fields = set(data).difference(valid_fields)

    if unknown_fields:
        raise ValueError(
            f"unknown fields for '{cls.__name__}': {unknown_fields}; valid fields : "
            f"{sorted(valid_fields)}"
        )


@dataclass(frozen=True, slots=True)
class Columns:
    depth: str = COL_DEPTH
    qt: str = COL_QT
    fs: str = COL_FS
    fr: str = COL_FR
    sv_eff: str = COL_SV_EFF
    sv_tot: str = COL_SV_TOT

    qt_inv: str = COL_QT_INV
    fs_inv: str = COL_FS_INV
    convg: str = COL_CONVG_INV

    def __post_init__(self):
        names = [getattr(self, field.name) for field in dataclasses.fields(self)]
        repeated = sorted({name for name in names if names.count(name) > 1})

        if repeated:
            raise ValueError(f"column names must be distinct; got repeated {repeated}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)
