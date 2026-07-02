from conic.engine import Configurator
from conic.engine._pipeliner import Operation, Step, bind
from conic.processing import _cleansing


def filter_input_columns() -> Operation:
    def build(config: Configurator) -> Step:
        input_columns = config.columns.input

        return bind(
            _cleansing.filter_input_columns,
            col_depth=input_columns.depth,
            col_qc=input_columns.qc,
            col_fs=input_columns.fs,
            col_u2=input_columns.u2,
            col_u0=input_columns.u0,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
        )

    return Operation(build)


def adjust_depth_spacing() -> Operation:
    def build(config: Configurator) -> Step:
        input_columns = config.columns.input
        cleansing = config.cleansing

        return bind(
            _cleansing.adjust_depth_spacing,
            start_depth=cleansing.start_depth,
            spacing=cleansing.spacing,
            col_depth=input_columns.depth,
        )

    return Operation(build)


def align_sleeve_column() -> Operation:
    def build(config: Configurator) -> Step:
        cleansing = config.cleansing

        if cleansing.max_sleeve_offset == 0:
            return Step(name="align_sleeve_column", apply=lambda lazy: lazy)

        input_columns = config.columns.input

        return bind(
            _cleansing.align_sleeve_column,
            col_depth=input_columns.depth,
            col_qc=input_columns.qc,
            col_fs=input_columns.fs,
            max_sleeve_offset=cleansing.max_sleeve_offset,
            indicators=cleansing.indicators,
        )

    return Operation(build)


def clean_by_indicators() -> Operation:
    def build(config: Configurator) -> Step:
        cleansing = config.cleansing

        return bind(
            _cleansing.clean_by_indicators,
            indicators=cleansing.indicators,
            mode=cleansing.clean_mode,
        )

    return Operation(build)


def floor_input_columns() -> Operation:
    def build(config: Configurator) -> Step:
        settings = config.settings
        input_columns = config.columns.input

        return bind(
            _cleansing.floor_input_columns,
            col_sv_eff=input_columns.sv_eff,
            col_qc=input_columns.qc,
            col_fs=input_columns.fs,
            p_ref=settings.p_ref,
        )

    return Operation(build)


def compute_hydrostatic_column(*, override: bool = False) -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input

        return bind(
            _cleansing.compute_hydrostatic_column,
            water_level=parameters.water_level,
            gamma_water=parameters.gamma_water,
            col_depth=input_columns.depth,
            col_u0=input_columns.u0,
            override=override,
        )

    return Operation(build)


def compute_geostatic_columns(*, override: bool = False) -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input

        return bind(
            _cleansing.compute_geostatic_columns,
            gamma_soil=parameters.gamma_soil,
            col_depth=input_columns.depth,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
            col_u0=input_columns.u0,
            override=override,
        )

    return Operation(build)
