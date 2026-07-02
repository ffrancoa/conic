import dataclasses
from dataclasses import dataclass
from typing import Any, Self

from conic.tools.inverse_filter._defaults import (
    COL_CONVG_INV,
    COL_FS_INV,
    COL_QT_INV,
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
    qt_inv: str = COL_QT_INV
    fs_inv: str = COL_FS_INV
    convg: str = COL_CONVG_INV

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)
