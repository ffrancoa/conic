import polars as pl

from conic.workflow import Configurator, Pipeliner


def process_standard(data: pl.DataFrame, config: Configurator) -> pl.DataFrame:
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

    Returns
    -------
    pl.DataFrame
        Processed sounding with all derived columns
        appended.

    Examples
    --------
    >>> config = build_configurator("config.toml")
    >>> result = process_standard(raw_data, config)
    """
    return Pipeliner.standard(config).run(data)
