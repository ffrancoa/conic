from conic.engine.pipeline import Operation


def sanitize_columns() -> Operation:
    return Operation(build=lambda catalog: catalog.sanitize_columns())


def adjust_depth_spacing() -> Operation:
    return Operation(build=lambda catalog: catalog.adjust_depth_spacing())


def clean_by_indicators() -> Operation:
    return Operation(build=lambda catalog: catalog.clean_by_indicators())


def compute_hydrostatic_column(*, override: bool) -> Operation:
    return Operation(
        build=lambda catalog: catalog.compute_hydrostatic_column(override=override)
    )


def compute_geostatic_columns(*, override: bool) -> Operation:
    return Operation(
        build=lambda catalog: catalog.compute_geostatic_columns(override=override)
    )


def compute_non_normalized_columns() -> Operation:
    return Operation(build=lambda catalog: catalog.compute_non_normalized_columns())


def compute_rolling_columns() -> Operation:
    return Operation(build=lambda catalog: catalog.compute_rolling_columns())


def compute_normalized_columns() -> Operation:
    return Operation(build=lambda catalog: catalog.compute_normalized_columns())


def compute_behavior_columns() -> Operation:
    return Operation(build=lambda catalog: catalog.compute_behavior_columns())
