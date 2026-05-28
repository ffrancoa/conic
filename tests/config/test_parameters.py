import pytest
from pydantic import ValidationError

from conic.config import Configurator


def test_copy_with_gamma_soil():
    config_a = Configurator()
    config_b = config_a.with_gamma_soil(18.5)

    assert config_b.parameters.gamma_soil == 18.5


def test_copy_water_level():
    config_a = Configurator()
    config_b = config_a.with_water_level(0)

    assert config_b.parameters.water_level == 0.0


def test_validate_with_area_ratio():
    p = Configurator()

    with pytest.raises(ValidationError):
        p.with_area_ratio(3)


def test_validate_gamma_water():
    p = Configurator()

    with pytest.raises(ValidationError):
        p.with_gamma_water(0.0)


def test_validate_with_water_level():
    p = Configurator()

    with pytest.raises(ValidationError):
        p.with_water_level(-1.0)
