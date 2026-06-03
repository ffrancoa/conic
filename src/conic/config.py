import tomllib
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NegativeFloat,
    NonNegativeFloat,
    PositiveFloat,
)

from conic._canonical import (
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
    COL_U0,
    COL_U2,
    GAMMA_WATER,
    ROLLING,
    ROLLING_LABEL,
)

type ColumnName = Annotated[str, Field(max_length=50)]
type CleanMode = Literal["replace", "remove"]
type Indicators = list[NegativeFloat]
type RollingValue = Literal[1, 3, 5]
type UnitRatio = Annotated[float, Field(gt=0.0, le=1.0)]


class Parameters(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    area_ratio: UnitRatio = AREA_RATIO
    rolling: RollingValue = ROLLING
    rolling_label: str = ROLLING_LABEL

    gamma_water: PositiveFloat = GAMMA_WATER
    gamma_soil: PositiveFloat | None = None
    water_level: NonNegativeFloat | None = None


class InputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    depth: ColumnName = COL_DEPTH
    qc: ColumnName = COL_QC
    fs: ColumnName = COL_FS
    u2: ColumnName = COL_U2

    u0: ColumnName = COL_U0
    sv_tot: ColumnName = COL_SV_TOT
    sv_eff: ColumnName = COL_SV_EFF


class OutputColumns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    qt: ColumnName = COL_QT
    qn: ColumnName = COL_QN

    qt1: ColumnName = COL_QT1
    rf: ColumnName = COL_RF
    fr: ColumnName = COL_FR
    bq: ColumnName = COL_BQ

    n: ColumnName = COL_N
    qtn: ColumnName = COL_QTN
    ic: ColumnName = COL_IC
    convg: ColumnName = COL_CONVG

    cd: ColumnName = COL_CD
    ib: ColumnName = COL_IB


class Columns(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    input: InputColumns = Field(default_factory=InputColumns)
    output: OutputColumns = Field(default_factory=OutputColumns)


class Cleansing(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_depth: NonNegativeFloat | None = None
    spacing: PositiveFloat | None = None

    indicators: Indicators = Field(default_factory=lambda: list())
    clean_mode: CleanMode = CLEAN_MODE


class Configurator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    columns: Columns = Field(default_factory=Columns)
    parameters: Parameters = Field(default_factory=Parameters)
    cleansing: Cleansing = Field(default_factory=Cleansing)

    def _with_field(self, submodel_name: str, field_name: str, value: object) -> Self:
        submodel = getattr(self, submodel_name)

        new_submodel_dict = submodel.model_dump() | {field_name: value}
        new_submodel = type(submodel)(**new_submodel_dict)

        return self.model_copy(update={submodel_name: new_submodel})

    def with_area_ratio(self, value: UnitRatio) -> Self:
        return self._with_field("parameters", "area_ratio", value)

    def with_rolling(self, value: RollingValue) -> Self:
        return self._with_field("parameters", "rolling", value)

    def with_gamma_water(self, value: PositiveFloat) -> Self:
        return self._with_field("parameters", "gamma_water", value)

    def with_gamma_soil(self, value: PositiveFloat | None) -> Self:
        return self._with_field("parameters", "gamma_soil", value)

    def with_water_level(self, value: NonNegativeFloat | None) -> Self:
        return self._with_field("parameters", "water_level", value)

    def with_start_depth(self, value: NonNegativeFloat | None) -> Self:
        return self._with_field("cleansing", "start_depth", value)

    def with_spacing(self, value: PositiveFloat | None) -> Self:
        return self._with_field("cleansing", "spacing", value)

    def with_indicators(self, values: list[float]) -> Self:
        return self._with_field("cleansing", "indicators", values)

    def with_clean_mode(self, value: CleanMode) -> Self:
        return self._with_field("cleansing", "clean_mode", value)

    @classmethod
    def from_toml(cls, file_path: Path | str) -> Self:
        with Path(file_path).open("rb") as file:
            config = tomllib.load(file)
        return cls.model_validate(config)
