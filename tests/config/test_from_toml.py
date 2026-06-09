from textwrap import dedent

import pytest

from conic.engine.config import Configurator


def test_read_from_toml(tmp_path):
    toml_content = dedent("""
        [parameters]
        gamma_water = 9.99
        water_level = 5.0
        area_ratio = 0.85

        [cleansing]
        clean_mode = "remove"
    """)

    toml_path = tmp_path / "conic.toml"
    toml_path.write_text(toml_content)

    config = Configurator.from_toml(toml_path)

    assert config.parameters.gamma_water == 9.99
    assert config.cleansing.clean_mode == "remove"


def test_validate_from_toml(tmp_path):
    toml_content = dedent("""
        [parameters]
        area_ratio = 1.05
    """)

    toml_path = tmp_path / "conic.toml"
    toml_path.write_text(toml_content)

    with pytest.raises(ValueError):
        _ = Configurator.from_toml(toml_path)
