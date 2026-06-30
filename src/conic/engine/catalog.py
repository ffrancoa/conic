from conic.core import correlations
from conic.core.calculate import derive, prepare
from conic.core.correlations import _boulanger2014 as bi14
from conic.core.correlations import _olson2002 as os02
from conic.core.correlations import _robertson2021 as r21
from conic.engine.config import Configurator
from conic.engine.step import Operation, Step, bind

# -------------------------------------------------------------------------------------
# Core operations (see `conic.core` for more information)
# -------------------------------------------------------------------------------------


def filter_input_columns() -> Operation:
    def build(config: Configurator) -> Step:
        input_columns = config.columns.input

        return bind(
            prepare.filter_input_columns,
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
            prepare.adjust_depth_spacing,
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
            prepare.align_sleeve_column,
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
            prepare.clean_by_indicators,
            indicators=cleansing.indicators,
            mode=cleansing.clean_mode,
        )

    return Operation(build)


def floor_input_columns() -> Operation:
    def build(config: Configurator) -> Step:
        settings = config.settings
        input_columns = config.columns.input

        return bind(
            prepare.floor_input_columns,
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
            prepare.compute_hydrostatic_column,
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
            prepare.compute_geostatic_columns,
            gamma_soil=parameters.gamma_soil,
            col_depth=input_columns.depth,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
            col_u0=input_columns.u0,
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
            col_qt_rol=output_columns.qt + parameters.rolling_label,
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
        )

    return Operation(build)


# -------------------------------------------------------------------------------------
# Correlation operations (see `conic.correlations` for more information)
# -------------------------------------------------------------------------------------


def add_r21_columns(*, max_su_liq_ratio: float = r21.MAX_SU_LIQ_RATIO) -> Operation:
    def build(config: Configurator) -> Step:
        output_columns = config.columns.output
        correlation_columns = config.columns.correlation.r21

        return bind(
            correlations.add_r21_columns,
            col_fr=output_columns.fr,
            col_qtn=output_columns.qtn,
            col_ic=output_columns.ic,
            col_kc=correlation_columns.kc,
            col_qtncs=correlation_columns.qtncs,
            col_su_liq_ratio=correlation_columns.su_liq_ratio,
            max_su_liq_ratio=max_su_liq_ratio,
        )

    return Operation(build)


def add_os02_columns(
    *,
    envelope: str = os02.DEFAULT_ENVELOPE,
    max_su_liq_ratio: float = os02.MAX_SU_LIQ_RATIO,
) -> Operation:

    def build(config: Configurator) -> Step:
        parameters = config.parameters
        settings = config.settings
        input_columns = config.columns.input
        output_columns = config.columns.output
        correlation_columns = config.columns.correlation.os02

        return bind(
            correlations.add_os02_columns,
            col_sv_eff=input_columns.sv_eff,
            col_qt_rol=output_columns.qt + parameters.rolling_label,
            col_qc1=correlation_columns.qc1,
            col_su_liq_ratio=correlation_columns.su_liq_ratio,
            p_ref=settings.p_ref,
            envelope=envelope,
            max_su_liq_ratio=max_su_liq_ratio,
        )

    return Operation(build)


def add_bi14_columns(
    *,
    envelope: str | None = bi14.DEFAULT_ENVELOPE,
    fitting_term: float | None = None,
) -> Operation:

    def build(config: Configurator) -> Step:
        parameters = config.parameters
        settings = config.settings
        input_columns = config.columns.input
        output_columns = config.columns.output
        correlation_columns = config.columns.correlation.bi14

        return bind(
            correlations.add_bi14_columns,
            col_ic=output_columns.ic,
            col_sv_eff=input_columns.sv_eff,
            col_qt_rol=output_columns.qt + parameters.rolling_label,
            col_fc=correlation_columns.fc,
            col_m=correlation_columns.m,
            col_qc1n=correlation_columns.qc1n,
            col_qc1ncs=correlation_columns.qc1ncs,
            col_convg=correlation_columns.convg,
            envelope=envelope,
            fitting_term=fitting_term,
            p_ref=settings.p_ref,
            max_iter=settings.max_iter,
            tolerance=settings.tolerance,
        )

    return Operation(build)
