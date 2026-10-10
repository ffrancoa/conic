from conic.calculate import _derive
from conic.workflow._configurator import Configurator
from conic.workflow._step import Operation, Step, bind


def compute_non_normalized_columns() -> Operation:
    def build(config: Configurator) -> Step:
        parameters = config.parameters
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            _derive.compute_non_normalized_columns,
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
            _derive.compute_rolling_columns,
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
            _derive.compute_normalized_columns,
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
            _derive.compute_behavior_columns,
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
