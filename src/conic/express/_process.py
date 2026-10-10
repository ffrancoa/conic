import polars as pl

from conic.workflow import Configurator, Pipeliner
from conic.workflow._step import Operation


def process_standard(
    data: pl.DataFrame,
    config: Configurator,
    *,
    extras: tuple[Operation, ...] = (),
) -> pl.DataFrame:
    """Run the standard CPTu processing pipeline.

    Applies the full sequence of operations (filtering,
    depth adjustment, sleeve alignment, indicator cleaning,
    input flooring, hydrostatic and geostatic computation,
    non-normalized and normalized parameters, and soil
    behavior classification) in a single call.

    Parameters
    ----------
    data : pl.DataFrame
        Raw CPTu sounding data. Must contain at least
        ``depth``, ``qc``, ``fs``, and ``u2`` columns
        (names determined by the configuration).
    config : Configurator
        Processing configuration. Build one with
        ``build_configurator`` or ``Configurator.from_toml``.
    extras : tuple of Operation, default ()
        Catalog operations, such as correlations, run after
        the standard sequence in the given order.

    Returns
    -------
    pl.DataFrame
        Processed sounding with all derived columns
        appended.

    Raises
    ------
    TypeError
        If an element of ``extras`` is not a catalog
        operation.

    Examples
    --------
    >>> config = build_configurator("config.toml")
    >>> result = process_standard(raw_data, config)

    >>> result = process_standard(
    ...     raw_data, config, extras=(catalog.add_bi14_columns(),)
    ... )
    """
    return Pipeliner.standard(config, extras=extras).run(data)
