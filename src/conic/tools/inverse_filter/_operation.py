from conic.engine import Configurator
from conic.engine._pipeliner import Operation, Step, bind
from conic.tools.inverse_filter._columns import Columns
from conic.tools.inverse_filter._compute import compute_inverse_filter
from conic.tools.inverse_filter._config import Config


def operation() -> Operation:
    def build(config: Configurator) -> Step:
        tool_config = config.tools.get("inverse_filter")

        if tool_config is None:
            raise ValueError(
                "inverse_filter tool config not found in configurator; "
                "register it with `.with_tool('inverse_filter', Config(...))`"
            )

        if not isinstance(tool_config, Config):
            raise TypeError(
                f"expected inverse_filter Config, got {type(tool_config).__name__!r}"
            )

        columns = config.tools.get("inverse_filter_columns", Columns())

        if not isinstance(columns, Columns):
            raise TypeError(
                f"expected inverse_filter Columns, got {type(columns).__name__!r}"
            )

        settings = config.settings
        input_columns = config.columns.input
        output_columns = config.columns.output

        return bind(
            compute_inverse_filter,
            col_qt=output_columns.qt,
            col_fs=input_columns.fs,
            col_fr=output_columns.fr,
            col_sv_eff=input_columns.sv_eff,
            col_sv_tot=input_columns.sv_tot,
            col_qt_inv=columns.qt_inv,
            col_fs_inv=columns.fs_inv,
            col_convg=columns.convg,
            dc=tool_config.dc,
            dz=tool_config.dz,
            z50_ref=tool_config.z50_ref,
            mz=tool_config.mz,
            m50=tool_config.m50,
            mq=tool_config.mq,
            mt=tool_config.mt,
            p_ref=settings.p_ref,
            max_iter=settings.max_iter,
            tolerance=settings.tolerance,
            stall_tolerance=tool_config.stall_tolerance,
        )

    return Operation(build)
