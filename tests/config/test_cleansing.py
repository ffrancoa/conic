import pytest
from pydantic import ValidationError

from conic.engine.config import Configurator


def test_copy_with_start_depth():
    config_a = Configurator()
    config_b = config_a.with_start_depth(1)

    assert config_a is not config_b
    assert config_b.cleansing.start_depth == 1
    assert config_b.cleansing.start_depth == 1.0


def test_copy_with_spacing():
    config_a = Configurator()
    config_b = config_a.with_spacing(0.025)

    assert config_a is not config_b
    assert config_b.cleansing.spacing == 0.025


def test_copy_with_indicators():
    config_a = Configurator()
    config_b = config_a.with_indicators([-999])

    assert config_a is not config_b
    assert config_b.cleansing.indicators == [-999.0]


def test_parse_with_indicators():
    config_a = Configurator()
    config_b = config_a.with_indicators(["-999"])

    assert config_b.cleansing.indicators == [-999.0]


def test_validate_with_spacing():
    p = Configurator()

    with pytest.raises(ValidationError):
        p.with_spacing(0.0)
        p.with_spacing(-1)
