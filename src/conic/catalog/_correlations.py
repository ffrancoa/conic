from conic import correlations
from conic.correlations import _boulanger2014 as bi14
from conic.correlations import _olson2002 as os02
from conic.correlations import _robertson2021 as r21
from conic.engine import Configurator
from conic.engine._pipeliner import Operation, Step, bind


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
