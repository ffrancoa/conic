import pytest
from conic import Processor
from pydantic import ValidationError

def test_copy_with_start_depth():
    pr1 = Processor()
    pr2 = pr1.with_start_depth(1)

    assert pr1 is not pr2
    assert pr2.cleansing.start_depth == 1
    assert pr2.cleansing.start_depth == 1.0

def test_copy_with_spacing():
    pr1 = Processor()
    pr2 = pr1.with_spacing(0.025)

    assert pr1 is not pr2
    assert pr2.cleansing.spacing == .025

def test_copy_with_indicators():
    pr1 = Processor()
    pr2 = pr1.with_indicators([999])
    
    assert pr1 is not pr2
    assert pr2.cleansing.indicators == [999]
    assert pr2.cleansing.indicators == [999.0]
    
def test_parse_with_indicators():
    pr1 = Processor()
    pr2 = pr1.with_indicators(["-999"])
    
    assert pr2.cleansing.indicators == [-999.0]

def test_validate_with_spacing():
    pr = Processor()

    with pytest.raises(ValidationError):
        pr.with_spacing(0.0)
        pr.with_spacing(-1)

def test_validate_with_indicators():
    pr = Processor()

    with pytest.raises(ValidationError):
        pr.with_indicators(["None"])
        
