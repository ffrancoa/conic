import tomllib
from pathlib import Path
from typing import Annotated, Literal, Optional, Self, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NegativeFloat,
    NonNegativeFloat,
    PositiveFloat,
)

from ._canonical import (
    AREA_RATIO,
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
    COL_QT,
    COL_QTN,
    COL_SV_EFF,
    COL_SV_TOT,
    COL_U0,
    COL_U2,
    GAMMA_WATER,
    INDICATOR_ACTION
)


type ColumnName = Annotated[str, Field(max_length=50)]
type UnitRatio = Annotated[float, Field(gt=0.0, le=1.0)]
type Indicators = list[NegativeFloat]
type IndicatorAction = Literal["ignore", "replace", "remove"]


class InputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    depth: ColumnName = COL_DEPTH
    qc: ColumnName    = COL_QC
    fs: ColumnName    = COL_FS
    u2: ColumnName    = COL_U2

    u0: ColumnName     = COL_U0
    sv_tot: ColumnName = COL_SV_TOT
    sv_eff: ColumnName = COL_SV_EFF

class OutputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    qt: ColumnName = COL_QT
    fr: ColumnName = COL_FR
    bq: ColumnName = COL_BQ
    
    n: ColumnName     = COL_N
    qtn: ColumnName   = COL_QTN
    ic: ColumnName    = COL_IC
    convg: ColumnName = COL_CONVG

    cd: ColumnName = COL_CD
    ib: ColumnName = COL_IB

class Columns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    input: InputColumns = Field(default_factory=InputColumns)
    output: OutputColumns = Field(default_factory=OutputColumns)

class Parameters(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    area_ratio: UnitRatio = AREA_RATIO
    gamma_water: PositiveFloat = GAMMA_WATER
    gamma_soil: Optional[PositiveFloat] = None
    water_level: Optional[NonNegativeFloat] = None

class Cleansing(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_depth: Optional[NonNegativeFloat] = None
    spacing: Optional[PositiveFloat] = None
    
    indicators: Indicators = Field(default_factory=lambda: list())
    indicator_action: IndicatorAction = cast(IndicatorAction, INDICATOR_ACTION)

class Processor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    columns: Columns = Field(default_factory=Columns)
    parameters: Parameters = Field(default_factory=Parameters)
    cleansing: Cleansing = Field(default_factory=Cleansing)

    def with_area_ratio(self, value: UnitRatio) -> Self:
        new_parameters_dict = self.parameters.model_dump() | {"area_ratio": value}
        new_parameters = Parameters(**new_parameters_dict)
        return self.model_copy(update={"parameters": new_parameters})

    def with_gamma_water(self, value: PositiveFloat) -> Self:
        new_parameters_dict = self.parameters.model_dump() | {"gamma_water": value}
        new_parameters = Parameters(**new_parameters_dict)
        return self.model_copy(update={"parameters": new_parameters})

    def with_gamma_soil(self, value: Optional[PositiveFloat]) -> Self:
        new_parameters_dict = self.parameters.model_dump() | {"gamma_soil": value}
        new_parameters = Parameters(**new_parameters_dict)
        return self.model_copy(update={"parameters": new_parameters})

    def with_water_level(self, value: Optional[NonNegativeFloat]) -> Self:
        new_parameters_dict = self.parameters.model_dump() | {"water_level": value}
        new_parameters = Parameters(**new_parameters_dict)
        return self.model_copy(update={"parameters": new_parameters})

    def with_start_depth(self, value: Optional[NonNegativeFloat]) -> Self:
        new_cleansing_dict = self.cleansing.model_dump() | {"start_depth": value}
        new_cleansing = Cleansing(**new_cleansing_dict)
        return self.model_copy(update={"cleansing": new_cleansing})

    def with_spacing(self, value: Optional[PositiveFloat]) -> Self:
        new_cleansing_dict = self.cleansing.model_dump() | {"spacing": value}
        new_cleansing = Cleansing(**new_cleansing_dict)
        return self.model_copy(update={"cleansing": new_cleansing})

    def with_indicators(self, values: list[float]) -> Self:
        new_cleansing_dict = self.cleansing.model_dump() | {"indicators": list(values)}
        new_cleansing = Cleansing(**new_cleansing_dict)
        return self.model_copy(update={"cleansing": new_cleansing})

    def with_indicator_action(self, value: IndicatorAction) -> Self:
        new_cleansing_dict = self.cleansing.model_dump() | {"indicator_action": value}
        new_cleansing = Cleansing(**new_cleansing_dict)
        return self.model_copy(update={"cleansing": new_cleansing})

    @classmethod
    def from_toml(cls, file_path: Path | str) -> Self:
        with open(Path(file_path), "rb") as file:
            config = tomllib.load(file)
            return cls.model_validate(config)

