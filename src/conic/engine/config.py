import dataclasses
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from conic.engine._canonical import (
    AREA_RATIO,
    CLEAN_MODE,
    COL_BQ,
    COL_CD,
    COL_CONVG,
    COL_DEPTH,
    COL_FR,
    COL_FS,
    COL_IB,
    COL_IC,
    COL_N,
    COL_QC,
    COL_QN,
    COL_QT,
    COL_QT1,
    COL_QTN,
    COL_RF,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U,
    COL_U0,
    COL_U2,
    GAMMA_WATER,
    MAX_ITER,
    P_REF,
    ROLLING,
    ROLLING_LABEL,
    TOLERANCE,
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
class Parameters:
    area_ratio: float = AREA_RATIO
    rolling: int = ROLLING
    rolling_label: str = ROLLING_LABEL

    gamma_water: float = GAMMA_WATER
    gamma_soil: float | None = None
    water_level: float | None = None

    def __post_init__(self):
        if self.area_ratio < 0.0 or self.area_ratio > 1.0:
            raise ValueError(
                f"Piezocone area ratio must be a positive number lower than 1.0; got "
                f"'{self.area_ratio}'"
            )
        if self.rolling not in (1, 3, 5):
            raise ValueError(f"rolling value must be 1, 3 or 5; got '{self.rolling}'")

        if self.gamma_water <= 0.0:
            raise ValueError(
                f"water unit weight (`gamma_water`) must be a (reasonable) positive "
                f"number; got '{self.gamma_water}'"
            )
        if self.gamma_soil is not None and self.gamma_soil <= 0.0:
            raise ValueError(
                f"soil unit weight (`gamma_soil`) must be a (reasonable) positive "
                f"number; got '{self.gamma_soil}'"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)


@dataclass(frozen=True, slots=True)
class Cleansing:
    start_depth: float | None = None
    spacing: float | None = None

    indicators: list[float] = dataclasses.field(default_factory=list)
    clean_mode: str = CLEAN_MODE

    def __post_init__(self):
        if self.start_depth is not None and self.start_depth < 0.0:
            raise ValueError(
                f"start depth used for depth adjustment (`start_depth`) must be a "
                f"positive number lower than ; got '{self.start_depth}'"
            )
        if self.spacing is not None and self.spacing < 0.0:
            raise ValueError(
                f"depth spacing must be a positive number; got '{self.spacing}'"
            )

        if self.clean_mode not in ("remove", "replace"):
            raise ValueError(
                f"clean mode must be 'remove' o 'replace'; got '{self.clean_mode}'"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)


@dataclass(frozen=True, slots=True)
class Settings:
    p_ref: float = P_REF
    max_iter: int = MAX_ITER
    tolerance: float = TOLERANCE

    def __post_init__(self):
        if self.p_ref <= 0.0:
            raise ValueError(
                f"reference pressure (`p_ref`) must be a (reasonable) positive number; "
                f"got '{self.p_ref}'"
            )
        if self.max_iter < 2:
            raise ValueError(
                f"the maximum number of iterations (`max_iter`) must be at least 2, "
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


@dataclass(frozen=True, slots=True)
class InputColumns:
    depth: str = COL_DEPTH
    qc: str = COL_QC
    fs: str = COL_FS
    u2: str = COL_U2

    u0: str = COL_U0
    sv_tot: str = COL_SV_TOT
    sv_eff: str = COL_SV_EFF

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)


@dataclass(frozen=True, slots=True)
class OutputColumns:
    qt: str = COL_QT
    qn: str = COL_QN

    qt1: str = COL_QT1
    rf: str = COL_RF
    fr: str = COL_FR
    bq: str = COL_BQ
    u: str = COL_U

    n: str = COL_N
    qtn: str = COL_QTN
    ic: str = COL_IC
    convg: str = COL_CONVG

    cd: str = COL_CD
    ib: str = COL_IB

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        _validate_keys(cls, data)
        return cls(**data)


@dataclass(frozen=True, slots=True)
class Columns:
    input: InputColumns = dataclasses.field(default_factory=InputColumns)
    output: OutputColumns = dataclasses.field(default_factory=OutputColumns)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        _validate_keys(cls, data)

        if "input" in data and isinstance(data["input"], dict):
            data = data | {"input": InputColumns.from_dict(data["input"])}

        if "output" in data and isinstance(data["output"], dict):
            data = data | {"output": OutputColumns.from_dict(data["output"])}

        return cls(**data)


@dataclass
class Configurator:
    parameters: Parameters = dataclasses.field(default_factory=Parameters)
    cleansing: Cleansing = dataclasses.field(default_factory=Cleansing)
    settings: Settings = dataclasses.field(default_factory=Settings)
    columns: Columns = dataclasses.field(default_factory=Columns)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        _validate_keys(cls, data)

        if "parameters" in data and isinstance(data["parameters"], dict):
            data = data | {"parameters": Parameters.from_dict(data["parameters"])}

        if "cleansing" in data and isinstance(data["cleansing"], dict):
            data = data | {"cleansing": Cleansing.from_dict(data["cleansing"])}

        if "settings" in data and isinstance(data["settings"], dict):
            data = data | {"settings": Settings.from_dict(data["settings"])}

        if "columns" in data and isinstance(data["columns"], dict):
            data = data | {"columns": Columns.from_dict(data["columns"])}

        return cls(**data)

    @classmethod
    def from_toml(cls, file_path: Path | str) -> Self:
        with Path(file_path).open("rb") as file:
            config = tomllib.load(file)

        return cls.from_dict(config)

    def _with_field(self, subclass_name: str, field_name: str, value: object) -> Self:
        subclass = getattr(self, subclass_name)

        new_data = dataclasses.asdict(subclass) | {field_name: value}
        new_subclass = type(subclass).from_dict(new_data)

        return dataclasses.replace(self, **{subclass_name: new_subclass})

    def with_area_ratio(self, value: float) -> Self:
        return self._with_field("parameters", "area_ratio", value)

    def with_rolling(self, value: int) -> Self:
        return self._with_field("parameters", "rolling", value)

    def with_gamma_water(self, value: float) -> Self:
        return self._with_field("parameters", "gamma_water", value)

    def with_gamma_soil(self, value: float | None) -> Self:
        return self._with_field("parameters", "gamma_soil", value)

    def with_water_level(self, value: float | None) -> Self:
        return self._with_field("parameters", "water_level", value)

    def with_start_depth(self, value: float | None) -> Self:
        return self._with_field("cleansing", "start_depth", value)

    def with_spacing(self, value: float | None) -> Self:
        return self._with_field("cleansing", "spacing", value)

    def with_indicators(self, values: list[float]) -> Self:
        return self._with_field("cleansing", "indicators", values)

    def with_clean_mode(self, value: str) -> Self:
        return self._with_field("cleansing", "clean_mode", value)

    def with_p_ref(self, value: str) -> Self:
        return self._with_field("settings", "p_ref", value)

    def with_max_iter(self, value: str) -> Self:
        return self._with_field("settings", "max_iter", value)

    def with_tolerance(self, value: str) -> Self:
        return self._with_field("settings", "tolerance", value)
