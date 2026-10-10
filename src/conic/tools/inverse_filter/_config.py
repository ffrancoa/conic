import dataclasses
from dataclasses import dataclass
from typing import Any, Self

from conic.tools.inverse_filter._defaults import (
    DC,
    KERNEL_EXTENT,
    M50,
    MAX_ITER,
    MQ,
    MT,
    MZ,
    P_REF,
    TOLERANCE,
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
    z50_ref: float = Z50_REF
    mz: float = MZ
    m50: float = M50
    mq: float = MQ
    mt: float = MT
    kernel_extent: float | None = KERNEL_EXTENT
    p_ref: float = P_REF
    max_iter: int = MAX_ITER
    tolerance: float = TOLERANCE

    def __post_init__(self):
        if self.dc <= 0.0:
            raise ValueError(
                f"cone diameter (`dc`) must be a positive number; got '{self.dc}'"
            )

        if self.z50_ref <= 0.0:
            raise ValueError(
                f"reference filter extension (`z50_ref`) must be a positive "
                f"number; got '{self.z50_ref}'"
            )

        if self.mt < 0.0:
            raise ValueError(
                f"interface rate threshold (`mt`) must be a non-negative number, "
                f"0.0 disables the interface correction; got '{self.mt}'"
            )

        if self.kernel_extent is not None and self.kernel_extent <= 0.0:
            raise ValueError(
                f"kernel half-width (`kernel_extent`) must be a positive number of "
                f"cone diameters or None for the full kernel; got "
                f"'{self.kernel_extent}'"
            )

        if self.p_ref <= 0.0:
            raise ValueError(
                f"reference pressure (`p_ref`) must be a (reasonable) positive number; "
                f"got '{self.p_ref}'"
            )

        if self.max_iter < 1:
            raise ValueError(
                f"the maximum number of iterations (`max_iter`) must be at least 1, "
                f"got '{self.max_iter}'"
            )

        if self.tolerance >= 1.0:
            raise ValueError(
                f"convergence tolerance must be less than 1.0, got '{self.tolerance}'"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)
