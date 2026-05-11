import pytest
from conic import Processor
from pydantic import ValidationError

def test_copy_with_gamma_soil():
    pr1 = Processor()
    pr2 = pr1.with_gamma_soil(18.5)

    assert pr2.parameters.gamma_soil == 18.5

def test_copy_water_level():
    pr1 = Processor()
    pr2 = pr1.with_water_level(0)

    assert pr2.parameters.water_level == 0.0

def test_validate_with_area_ratio():
    pr = Processor()
    
    with pytest.raises(ValidationError):
        pr.with_area_ratio(3)

def test_validate_gamma_water():
    pr = Processor()

    with pytest.raises(ValidationError):
        pr.with_gamma_water(0.0)

def test_validate_with_water_level():
    pr = Processor()

    with pytest.raises(ValidationError):
        pr.with_water_level(-1.0)

