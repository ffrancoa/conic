import tomllib
from pathlib import Path
from typing import Annotated, Literal, Optional, Self

from pydantic import BaseModel, ConfigDict, Field
from pydantic import PositiveFloat, NonNegativeFloat


type ColumnName = Annotated[str, Field(max_length=50)]
type UnitRatio = Annotated[float, Field(gt=0.0, le=1.0)]
type IndicatorAction = Literal["ignore", "replace", "remove"]

def default_indicators() -> list[float]:
    return [-9999.0, -8888.0, -7777.0]


class InputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    depth: ColumnName = "Depth (m)"
    qc: ColumnName = "qc (MPa)"
    fs: ColumnName = "fs (kPa)"
    u2: ColumnName = "u2 (kPa)"

    u0: ColumnName = "u0 (kPa)"
    sv_tot: ColumnName = "σv tot (kPa)"
    sv_eff: ColumnName = "σv eff (kPa)"

class OutputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    qt: ColumnName = "qt (MPa)"
    fr: ColumnName = "Fr (%)"
    bq: ColumnName = "Bq (-)"
    
    n_exp: ColumnName = "n exp. (-)"
    qtn: ColumnName = "Qtn (-)"
    ic: ColumnName = "Ic (-)"
    conv: ColumnName = "converged (-)"
    cd: ColumnName = "CD (-)"
    ib: ColumnName = "IB (-)"

class Columns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    input: InputColumns = Field(default_factory=InputColumns)
    output: OutputColumns = Field(default_factory=OutputColumns)

class Parameters(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    area_ratio: UnitRatio = 0.80
    gamma_water: PositiveFloat = 9.81
    gamma_soil: Optional[PositiveFloat] = None
    water_level: Optional[NonNegativeFloat] = None

class Cleansing(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_depth: Optional[NonNegativeFloat] = None
    spacing: Optional[PositiveFloat] = None
    
    indicators: list[float] = Field(default_factory=default_indicators)
    indicator_action: IndicatorAction = "ignore"

class Processor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    columns: Columns = Field(default_factory=Columns)
    parameters: Parameters = Field(default_factory=Parameters)
    cleansing: Cleansing = Field(default_factory=Cleansing)

    def with_area_ratio(self, value: UnitRatio) -> Self:
        new_parameters = self.parameters.model_copy(update={"area_ratio": value})
        return self.model_copy(update={"parameters": new_parameters})

    def with_gamma_water(self, value: PositiveFloat) -> Self:
        new_parameters = self.parameters.model_copy(update={"gamma_water": value})
        return self.model_copy(update={"parameters": new_parameters})

    def with_gamma_soil(self, value: Optional[PositiveFloat]) -> Self:
        new_parameters = self.parameters.model_copy(update={"gamma_soil": value})
        return self.model_copy(update={"parameters": new_parameters})

    def with_water_level(self, value: Optional[NonNegativeFloat]) -> Self:
        new_parameters = self.parameters.model_copy(update={"water_level": value})
        return self.model_copy(update={"parameters": new_parameters})

    def with_start_depth(self, value: Optional[NonNegativeFloat]) -> Self:
        new_cleansing = self.cleansing.model_copy(update={"start_depth": value})
        return self.model_copy(update={"cleansing": new_cleansing})

    def with_spacing(self, value: Optional[PositiveFloat]) -> Self:
        new_cleansing = self.cleansing.model_copy(update={"spacing": value})
        return self.model_copy(update={"cleansing": new_cleansing})

    def with_indicators(self, values: list[float]) -> Self:
        new_cleasing = self.cleansing.model_copy(update={"indicators": list(values)})
        return self.model_copy(update={"cleansing": new_cleasing})

    def with_indicator_action(self, value: IndicatorAction) -> Self:
        new_cleansing = self.cleansing.model_copy(update={"indicator_action": value})
        return self.model_copy(update={"cleansing": new_cleansing})

    @classmethod
    def from_toml(cls, file_path: Path | str) -> Self:

        with open(Path(file_path), "rb") as file:
            config = tomllib.load(file)

            return cls.model_validate(config)

