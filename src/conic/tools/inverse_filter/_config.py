import dataclasses
from dataclasses import dataclass
from typing import Any, Self

from conic.tools.inverse_filter._defaults import (
    DC,
    DZ,
    M50,
    MQ,
    MT,
    MZ,
    STALL_TOLERANCE,
    Z50_REF,
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
class Config:
    dc: float = DC
    dz: float = DZ
    z50_ref: float = Z50_REF
    mz: float = MZ
    m50: float = M50
    mq: float = MQ
    mt: float = MT
    stall_tolerance: float = STALL_TOLERANCE

    def __post_init__(self):
        if self.dc <= 0.0:
            raise ValueError(
                f"cone diameter (`dc`) must be a positive number; got '{self.dc}'"
            )

        if self.dz <= 0.0:
            raise ValueError(
                f"data spacing (`dz`) must be a positive number; got '{self.dz}'"
            )

        if self.z50_ref <= 0.0:
            raise ValueError(
                f"reference filter extension (`z50_ref`) must be a positive "
                f"number; got '{self.z50_ref}'"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)
