import pytest
from conic import Processor
from pydantic import ValidationError

def test_copy_with_gamma_soil():
    p1 = Processor()
    p2 = p1.with_gamma_soil(18.5)

    assert p2.parameters.gamma_soil == 18.5

def test_copy_water_level():
    p1 = Processor()
    p2 = p1.with_water_level(0)

    assert p2.parameters.water_level == 0.0

def test_validate_with_area_ratio():
    p = Processor()
    
    with pytest.raises(ValidationError):
        p.with_area_ratio(3)

def test_validate_gamma_water():
    p = Processor()

    with pytest.raises(ValidationError):
        p.with_gamma_water(0.0)

def test_validate_with_water_level():
    p = Processor()

    with pytest.raises(ValidationError):
        p.with_water_level(-1.0)

