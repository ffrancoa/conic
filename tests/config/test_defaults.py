from conic import Processor

def test_default_columns():
    pr = Processor()

    assert pr.columns.input.depth == "Depth (m)"
    assert pr.columns.output.convg == "convg. (-)"
    
def test_default_parameters():
    pr = Processor()
    
    assert pr.parameters.area_ratio == 0.80
    assert pr.parameters.gamma_soil is None

def test_default_cleansing():
    pr = Processor()

    assert pr.cleansing.start_depth is None
    assert pr.cleansing.spacing is None
    
    assert pr.cleansing.indicators == [-9999, -8888, -7777]
    assert pr.cleansing.indicator_action == "ignore"
