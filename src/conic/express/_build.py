import dataclasses
from pathlib import Path
from typing import Any

from conic.engine import Configurator, Pipeliner
from conic.engine._configurator import InputColumns, OutputColumns
from conic.engine._pipeliner import Operation

INPUT_COLUMNS = {field.name for field in dataclasses.fields(InputColumns)}
OUTPUT_COLUMNS = {field.name for field in dataclasses.fields(OutputColumns)}


def _classify_columns(columns: dict[str, str]) -> dict[str, dict[str, str]]:
    unknown_columns = set(columns).difference(INPUT_COLUMNS, OUTPUT_COLUMNS)

    if unknown_columns:
        raise ValueError(f"unknown column keys: {unknown_columns}.")

    input_columns = {}
    output_columns = {}

    for key, name in columns.items():
        if key in INPUT_COLUMNS:
            input_columns[key] = name
        else:
            output_columns[key] = name

    return {"input": input_columns, "output": output_columns}


def build_configurator(
    config_file: Path | str | None = None,
    *,
    parameters: dict[str, float] | None = None,
    cleansing: dict[str, Any] | None = None,
    settings: dict[str, int | float] | None = None,
    columns: dict[str, str] | None = None,
) -> Configurator:
    """Create a custom Configurator from defaults, TOML file, or overrides.

    Starts from defaults (or a TOML file) and applies any
    keyword overrides on top. Overrides are merged
    per-section, so only the fields that differ from the
    base need to be specified.

    Column names can be passed as a flat dict using the
    canonical field names (e.g. ``depth``, ``qc``, ``qt``);
    input and output columns are classified automatically.

    Parameters
    ----------
    config_file : Path, str, or None, default None
        Path to a TOML configuration file. When ``None``,
        all-defaults configuration is used as the base.
    parameters : dict or None, optional
        Overrides for physical parameters (e.g.
        ``gamma_soil``, ``gamma_water``).
    cleansing : dict or None, optional
        Overrides for data cleansing (e.g. ``indicators``,
        ``clean_mode``).
    settings : dict or None, optional
        Overrides for algorithm settings (e.g.
        ``max_iter``, ``tolerance``).
    columns : dict or None, optional
        Column name overrides as ``{field: name}`` pairs
        (e.g. ``{"u2": "u (kPa)"}``). Unknown field names
        raise ``ValueError``.

    Returns
    -------
    Configurator
        Ready-to-use configuration instance.

    Raises
    ------
    ValueError
        If ``columns`` contains a key that does not match
        any known input or output field.

    Examples
    --------
    >>> config = build_configurator("conic.toml")

    >>> config = build_configurator(
    ...     parameters={"gamma_soil": 19.5},
    ...     columns={"u2": "u (kPa)"},
    ... )
    """
    config = Configurator.from_toml(config_file) if config_file else Configurator()

    overrides: dict[str, Any] = {}

    if parameters is not None:
        overrides["parameters"] = dataclasses.asdict(config.parameters) | parameters

    if cleansing is not None:
        overrides["cleansing"] = dataclasses.asdict(config.cleansing) | cleansing

    if settings is not None:
        overrides["settings"] = dataclasses.asdict(config.settings) | settings

    if columns is not None:
        classified = _classify_columns(columns)
        columns_dump = dataclasses.asdict(config.columns)
        columns_dump["input"] |= classified["input"]
        columns_dump["output"] |= classified["output"]
        overrides["columns"] = columns_dump

    if not overrides:
        return config

    return Configurator.from_dict(dataclasses.asdict(config) | overrides)


def build_pipeliner(
    *, config: Configurator | Path | str, steps: tuple[Operation, ...]
) -> Pipeliner:
    """Create a custom Pipeliner from a sequence of catalog operations.

    Use this instead of ``process_standard`` when only a
    subset of operations is needed or when the execution
    order must differ from the standard pipeline.

    Parameters
    ----------
    config : Configurator, Path, or str
        Processing configuration. Accepts a
        ``Configurator`` instance or a path to a TOML
        file (which is loaded automatically).
    steps : tuple of Operation
        Ordered sequence of operations to execute.
        Available operations are exposed in
        ``conic.catalog``.

    Returns
    -------
    Pipeliner
        Pipeline instance ready to run via ``.run(data)``.

    Examples
    --------
    >>> from conic import catalog
    >>> pipe = build_pipeliner(
    ...     config="conic.toml",
    ...     steps=(
    ...         catalog.filter_input_columns(),
    ...         catalog.compute_non_normalized_columns(),
    ...     ),
    ... )
    >>> result = pipe.run(raw_data)
    """
    if not isinstance(config, Configurator):
        config = Configurator.from_toml(config)

    return Pipeliner.from_operations(config, steps)
