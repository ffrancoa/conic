import polars as pl

from conic._utils import check_required_columns, has_column


def _expr_estimate_mean_spacing(col_depth: str, digits: int = 3) -> pl.Expr:
    return (
        (pl.col(col_depth).last() - pl.col(col_depth).first()) / (pl.len() - 1)
    ).round(digits)


def _expr_estimate_sleeve_offset(
    col_qc: str, col_fs: str, max_sleeve_offset: int, indicators: list[float] | None
) -> pl.Expr:

    cleaned_qc_column = pl.col(col_qc).fill_nan(None)
    cleaned_fs_column = pl.col(col_fs).fill_nan(None)

    if indicators:
        cleaned_qc_column = _expr_replace_indicators(
            cleaned_qc_column, indicators, None
        )
        cleaned_fs_column = _expr_replace_indicators(
            cleaned_fs_column, indicators, None
        )

    window_size = 2 * max_sleeve_offset + 1

    detrended_qc_column = cleaned_qc_column - cleaned_qc_column.rolling_mean(
        window_size, center=True
    )
    detrended_fs_column = cleaned_fs_column - cleaned_fs_column.rolling_mean(
        window_size, center=True
    )

    pearson_correlations = pl.concat_list(
        [
            pl.corr(detrended_qc_column, detrended_fs_column.shift(lag))
            for lag in range(-max_sleeve_offset, max_sleeve_offset + 1)
        ]
    )

    max_correlation = pearson_correlations.list.max()
    max_correlation_index = pearson_correlations.list.arg_max().cast(pl.Int64)

    return (
        pl.when(max_correlation.is_nan() | max_correlation.is_null())
        .then(pl.lit(0, dtype=pl.Int64))  # no correlation (i.e., offset = 0)
        .otherwise(max_correlation_index - max_sleeve_offset)
    )


def _expr_replace_indicators(
    target_columns: pl.Expr,
    indicators: list[float],
    value: float | None,
) -> pl.Expr:

    return (
        pl.when(target_columns.is_in(indicators)).then(value).otherwise(target_columns)
    )


def _remove_rows_with_indicators(
    lazy: pl.LazyFrame, target_columns: pl.Expr, indicators: list[float]
) -> pl.LazyFrame:

    mask = target_columns.is_in(indicators)
    global_mask = pl.any_horizontal(mask).not_()

    return lazy.filter(global_mask)


def adjust_depth_spacing(
    lazy: pl.LazyFrame,
    col_depth: str,
    *,
    start_depth: float | None,
    spacing: float | None,
    digits: int = 3,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_depth})

    start_depth_expr = (
        pl.lit(start_depth) if start_depth is not None else pl.col(col_depth).first()
    )

    spacing_expr = (
        pl.lit(spacing)
        if spacing is not None
        else _expr_estimate_mean_spacing(col_depth, digits)
    )

    return lazy.with_columns(
        (start_depth_expr + pl.int_range(pl.len()) * spacing_expr)
        .round(digits)
        .alias(col_depth)
    )


def align_sleeve_column(
    lazy: pl.LazyFrame,
    col_depth: str,
    col_qc: str,
    col_fs: str,
    *,
    max_sleeve_offset: int,
    indicators: list[float] | None = None,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_depth, col_qc, col_fs})

    if max_sleeve_offset <= 0:
        raise ValueError(
            f"maximum sleeve offset must be a positive integer; got "
            f"{max_sleeve_offset!r}"
        )

    sleeve_offset_column = _expr_estimate_sleeve_offset(
        col_qc, col_fs, max_sleeve_offset, indicators
    )

    return lazy.with_columns(pl.col(col_fs).shift(sleeve_offset_column.first()))


def clean_by_indicators(
    lazy: pl.LazyFrame,
    *,
    indicators: list[float] | None,
    mode: str,
    replace_value: float = float("nan"),
) -> pl.LazyFrame:

    if indicators:
        target_columns = pl.selectors.numeric()

        match mode:
            case "replace":
                return lazy.with_columns(
                    _expr_replace_indicators(
                        target_columns, indicators, replace_value
                    ).name.keep()
                )
            case "remove":
                return _remove_rows_with_indicators(lazy, target_columns, indicators)
            case _:
                raise ValueError(
                    "invalid `action` argument; use only 'replace' or 'remove'"
                )
    else:
        return lazy


def floor_input_columns(
    lazy: pl.LazyFrame,
    col_qc: str,
    col_fs: str,
    col_sv_eff: str,
    *,
    p_ref: float,
) -> pl.LazyFrame:

    floor = 0.001 * p_ref

    target_columns = [col_qc, col_fs]

    if has_column(lazy, col_sv_eff):
        target_columns.append(col_sv_eff)

    return lazy.with_columns(
        pl.when(pl.col(col) == 0.0)
        .then(floor)
        .otherwise(pl.col(col))
        .alias(col)
        for col in target_columns
    )  # fmt: off


def compute_hydrostatic_column(
    lazy: pl.LazyFrame,
    col_depth: str,
    col_u0: str,
    *,
    water_level: float | None,
    gamma_water: float,
    override: bool = False,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_depth})

    if has_column(lazy, col_u0) and not override:
        raise ValueError(
            f"hydrostatic pressure ('{col_u0}') was already included in "
            f"this DataFrame; set `override=True` to override"
        )

    if water_level is None:
        data_with_u0 = lazy.with_columns(pl.lit(0.0).alias(col_u0))
    else:
        data_with_u0 = lazy.with_columns(
            pl.when(pl.col(col_depth) >= water_level)
            .then((pl.col(col_depth) - water_level) * gamma_water)
            .otherwise(0.0)
            .alias(col_u0)
        )

    return data_with_u0


def compute_geostatic_columns(
    lazy: pl.LazyFrame,
    col_depth: str,
    col_sv_eff: str,
    col_sv_tot: str,
    col_u0: str,
    *,
    gamma_soil: float | None,
    override: bool = False,
) -> pl.LazyFrame:

    check_required_columns(lazy, {col_depth})

    has_sv_eff = has_column(lazy, col_sv_eff)
    has_sv_tot = has_column(lazy, col_sv_tot)

    if has_sv_eff and has_sv_tot and not override:
        raise ValueError(
            f"geostatic columns ('{col_sv_eff}' and '{col_sv_tot}') were "
            f"already included in this DataFrame; set `override=True` to "
            f"override"
        )
    elif has_sv_tot and not has_sv_eff and not override:
        return lazy.with_columns(
            (pl.col(col_sv_tot) - pl.col(col_u0)).alias(col_sv_eff)
        )
    elif has_sv_eff and not has_sv_tot and not override:
        return lazy.with_columns(
            (pl.col(col_sv_eff) + pl.col(col_u0)).alias(col_sv_tot)
        )
    else:
        if gamma_soil is None or gamma_soil <= 0:
            raise ValueError(
                "a valid soil unit weight value (`gamma_soil`) must be "
                "provided to compute geostatic stresses"
            )
        return lazy.with_columns(
            (sv_tot_expr := pl.col(col_depth) * gamma_soil).alias(col_sv_tot),
            (sv_tot_expr - pl.col(col_u0)).alias(col_sv_eff),
        )


def filter_input_columns(
    lazy: pl.LazyFrame,
    col_depth: str,
    col_qc: str,
    col_fs: str,
    col_u2: str,
    col_u0: str,
    col_sv_eff: str,
    col_sv_tot: str,
) -> pl.LazyFrame:

    required_columns = [col_depth, col_qc, col_fs, col_u2]
    optional_columns = [col_u0, col_sv_eff, col_sv_tot]

    check_required_columns(lazy, set(required_columns))

    present_optional = [col for col in optional_columns if has_column(lazy, col)]

    return lazy.select(required_columns + present_optional)
