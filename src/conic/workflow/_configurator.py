import dataclasses
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from conic.workflow._sections import (
    Cleansing,
    Columns,
    Parameters,
    Settings,
    _validate_keys,
)


@dataclass
class Configurator:
    """Manage CPTu processing parameters, column names, and settings.

    Compose a configuration from code defaults, a TOML file, or
    a combination of both using ``from_dict`` or ``from_toml``.
    Individual values can be overridden after construction with
    the fluent ``with_*`` methods, each of which returns a new
    ``Configurator`` with the change applied.

    Parameters
    ----------
    parameters : Parameters
        Test parameters such as area ratio, rolling window,
        and unit weights.
    cleansing : Cleansing
        Data-cleaning rules: start depth, spacing, indicator
        values, cleaning mode, and sleeve alignment offset.
    settings : Settings
        Solver settings: reference pressure, maximum
        iterations, and convergence tolerance.
    columns : Columns
        Input, output, and correlation column name mappings.

    Examples
    --------
    >>> config = Configurator()
    >>> config = config.with_gamma_soil(18.0)

    >>> config = Configurator.from_toml("project.toml")
    """

    parameters: Parameters = dataclasses.field(default_factory=Parameters)
    cleansing: Cleansing = dataclasses.field(default_factory=Cleansing)
    settings: Settings = dataclasses.field(default_factory=Settings)
    columns: Columns = dataclasses.field(default_factory=Columns)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Configurator from a nested dictionary.

        Parameters
        ----------
        data : dict
            Nested mapping whose keys match the attribute
            names of ``Configurator`` and its sub-models.

        Returns
        -------
        Configurator

        Raises
        ------
        ValueError
            If any key is not a recognized field.
        """
        _validate_keys(cls, data)

        if "parameters" in data and isinstance(data["parameters"], dict):
            data = data | {"parameters": Parameters.from_dict(data["parameters"])}

        if "cleansing" in data and isinstance(data["cleansing"], dict):
            data = data | {"cleansing": Cleansing.from_dict(data["cleansing"])}

        if "settings" in data and isinstance(data["settings"], dict):
            data = data | {"settings": Settings.from_dict(data["settings"])}

        if "columns" in data and isinstance(data["columns"], dict):
            data = data | {"columns": Columns.from_dict(data["columns"])}

        return cls(**data)

    @classmethod
    def from_toml(cls, file_path: Path | str) -> Self:
        """Create a Configurator from a TOML file.

        Parameters
        ----------
        file_path : Path or str
            Path to a TOML configuration file whose keys
            match the attribute names of ``Configurator``
            and its sub-models.

        Returns
        -------
        Configurator

        Raises
        ------
        ValueError
            If any key is not a recognized field.
        FileNotFoundError
            If the file does not exist.
        """
        with Path(file_path).open("rb") as file:
            config = tomllib.load(file)

        return cls.from_dict(config)

    def _with_field(self, subclass_name: str, field_name: str, value: object) -> Self:
        subclass = getattr(self, subclass_name)

        new_data = dataclasses.asdict(subclass) | {field_name: value}
        new_subclass = type(subclass).from_dict(new_data)

        return dataclasses.replace(self, **{subclass_name: new_subclass})

    def with_area_ratio(self, value: float) -> Self:
        """Return a copy with a new piezocone area ratio."""
        return self._with_field("parameters", "area_ratio", value)

    def with_rolling(self, value: int) -> Self:
        """Return a copy with a new rolling window size."""
        return self._with_field("parameters", "rolling", value)

    def with_gamma_water(self, value: float) -> Self:
        """Return a copy with a new water unit weight."""
        return self._with_field("parameters", "gamma_water", value)

    def with_gamma_soil(self, value: float | None) -> Self:
        """Return a copy with a new soil unit weight."""
        return self._with_field("parameters", "gamma_soil", value)

    def with_water_level(self, value: float | None) -> Self:
        """Return a copy with a new water level depth."""
        return self._with_field("parameters", "water_level", value)

    def with_start_depth(self, value: float | None) -> Self:
        """Return a copy with a new start depth."""
        return self._with_field("cleansing", "start_depth", value)

    def with_spacing(self, value: float | None) -> Self:
        """Return a copy with a new depth spacing."""
        return self._with_field("cleansing", "spacing", value)

    def with_indicators(self, values: list[float]) -> Self:
        """Return a copy with new indicator values."""
        return self._with_field("cleansing", "indicators", values)

    def with_clean_mode(self, value: str) -> Self:
        """Return a copy with a new cleaning mode."""
        return self._with_field("cleansing", "clean_mode", value)

    def with_max_sleeve_offset(self, value: int) -> Self:
        """Return a copy with a new sleeve alignment offset."""
        return self._with_field("cleansing", "max_sleeve_offset", value)

    def with_p_ref(self, value: float) -> Self:
        """Return a copy with a new reference pressure."""
        return self._with_field("settings", "p_ref", value)

    def with_max_iter(self, value: int) -> Self:
        """Return a copy with a new iteration limit."""
        return self._with_field("settings", "max_iter", value)

    def with_tolerance(self, value: float) -> Self:
        """Return a copy with a new convergence tolerance."""
        return self._with_field("settings", "tolerance", value)
