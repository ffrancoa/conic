from pathlib import Path

import conic.workflow
from conic.workflow import Configurator

_DEFAULTS_TOML = Path(conic.workflow.__file__).parent / "defaults.toml"


def test_defaults_toml_matches_code_defaults():
    assert Configurator.from_toml(_DEFAULTS_TOML) == Configurator()


def test_defaults_toml_omits_optional_none_fields():
    config = Configurator.from_toml(_DEFAULTS_TOML)

    assert config.parameters.gamma_soil is None
    assert config.parameters.water_level is None
    assert config.cleansing.start_depth is None
    assert config.cleansing.spacing is None
