import pytest
from conic import Processor
from pydantic import ValidationError

def test_copy_with_start_depth():
    p1 = Processor()
    p2 = p1.with_start_depth(1)

    assert p1 is not p2
    assert p2.cleansing.start_depth == 1
    assert p2.cleansing.start_depth == 1.0

def test_copy_with_spacing():
    p1 = Processor()
    p2 = p1.with_spacing(0.025)

    assert p1 is not p2
    assert p2.cleansing.spacing == .025

def test_copy_with_indicators():
    p1 = Processor()
    p2 = p1.with_indicators([999])
    
    assert p1 is not p2
    assert p2.cleansing.indicators == [999.0]
    
def test_parse_with_indicators():
    p1 = Processor()
    p2 = p1.with_indicators(["-999"])
    
    assert p2.cleansing.indicators == [-999.0]

def test_validate_with_spacing():
    p = Processor()

    with pytest.raises(ValidationError):
        p.with_spacing(0.0)
        p.with_spacing(-1)
      
