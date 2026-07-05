from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    coefficient: float
    residual_std: float
    n_points: int

    def __len__(self) -> int:
        return self.n_points
