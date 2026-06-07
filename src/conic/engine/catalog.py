from conic.core.calculate import derive, prepare
from conic.core.correlate import compose
from conic.engine.config import Configurator
from conic.engine.step import Operation, Step, bind


def sanitize_columns() -> Operation:
    def build(config: Configurator) -> Step:
        columns = config.columns.input

        return bind(
            prepare.sanitize_columns,
            col_depth=columns.depth,
            col_qc=columns.qc,
            col_fs=columns.fs,
            col_u2=columns.u2,
            col_u0=columns.u0,
            col_sv_eff=columns.sv_eff,
            col_sv_tot=columns.sv_tot,
        )

    return Operation(build)


def adjust_depth_spacing() -> Operation:
    def build(config: Configurator) -> Step:
        columns = config.columns.input
        cleansing = config.cleansing

        return bind(
            prepare.adjust_depth_spacing,
            start_depth=cleansing.start_depth,
            spacing=cleansing.spacing,
            col_depth=columns.depth,
        )

    return Operation(build)


def clean_by_indicators() -> Operation:
    def build(config: Configurator) -> Step:
        cleansing = config.cleansing

        return bind(
            prepare.clean_by_indicators,
            indicators=cleansing.indicators,
            mode=cleansing.clean_mode,
        )

    return Operation(build)


def compute_hydrostatic_column(*, override: bool = False) -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        columns = config.columns.input

        return bind(
            prepare.compute_hydrostatic_column,
            water_level=parameters.water_level,
            gamma_water=parameters.gamma_water,
            col_depth=columns.depth,
            col_u0=columns.u0,
            override=override,
        )

    return Operation(build)


def compute_geostatic_columns(*, override: bool = False) -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        columns = config.columns.input

        return bind(
            prepare.compute_geostatic_columns,
            gamma_soil=parameters.gamma_soil,
            col_depth=columns.depth,
            col_sv_eff=columns.sv_eff,
            col_sv_tot=columns.sv_tot,
            col_u0=columns.u0,
            override=override,
        )

    return Operation(build)


def compute_non_normalized_columns() -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            derive.compute_non_normalized_columns,
            area_ratio=parameters.area_ratio,
            col_sv_tot=input_columns.sv_tot,
            col_u2=input_columns.u2,
            col_fs=input_columns.fs,
            col_qc=input_columns.qc,
            col_qt=output_columns.qt,
            col_qn=output_columns.qn,
            col_rf=output_columns.rf,
        )

    return Operation(build)


def compute_rolling_columns() -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            derive.compute_rolling_columns,
            rolling=parameters.rolling,
            col_fs=input_columns.fs,
            col_qt=output_columns.qt,
            col_qn=output_columns.qn,
            rolling_label=parameters.rolling_label,
        )

    return Operation(build)


def compute_normalized_columns() -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            derive.compute_normalized_columns,
            col_sv_eff=input_columns.sv_eff,
            col_u0=input_columns.u0,
            col_u2=input_columns.u2,
            col_fs=input_columns.fs,
            col_qn=output_columns.qn,
            col_qt1=output_columns.qt1,
            col_fr=output_columns.fr,
            col_bq=output_columns.bq,
            col_u=output_columns.u,
            rolling_label=parameters.rolling_label,
        )

    return Operation(build)


def compute_behavior_columns() -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        settings = config.settings
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            derive.compute_behavior_columns,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
            col_qt=output_columns.qt,
            col_fr=output_columns.fr,
            col_n=output_columns.n,
            col_qtn=output_columns.qtn,
            col_ic=output_columns.ic,
            col_convg=output_columns.convg,
            col_cd=output_columns.cd,
            col_ib=output_columns.ib,
            p_ref=settings.p_ref,
            max_iter=settings.max_iter,
            tolerance=settings.tolerance,
            rolling_label=parameters.rolling_label,
        )

    return Operation(build)


# ---


def add_r21_columns() -> Operation:
    def build(config: Configurator) -> Step:
        columns = config.columns.output

        return bind(
            compose.add_r21_columns,
            col_fr=columns.fr,
            col_qtn=columns.qtn,
            col_ic=columns.ic,
        )

    return Operation(build)


def add_os02_columns(*, bound: str = "mean") -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        settings = config.settings
        columns = config.columns.input

        return bind(
            compose.add_os02_columns,
            bound=bound,
            p_ref=settings.p_ref,
            rolling=parameters.rolling,
            col_sv_eff=columns.sv_eff,
            col_qc=columns.qc,
        )

    return Operation(build)
