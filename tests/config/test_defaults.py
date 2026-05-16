from conic import Processor


def test_default_columns():
    p = Processor()

    assert p.columns.input.depth == "Depth (m)"
    assert p.columns.output.convg == "convg. (-)"
    
def test_default_parameters():
    p = Processor()
    
    assert p.parameters.area_ratio == 0.80
    assert p.parameters.gamma_soil is None

def test_default_cleansing():
    p = Processor()

    assert p.cleansing.start_depth is None
    assert p.cleansing.spacing is None
    
    assert p.cleansing.indicators == []
    assert p.cleansing.indicator_action == "ignore"
