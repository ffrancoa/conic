from conic.workflow import Configurator


def test_default_columns():
    config = Configurator()

    assert config.columns.input.depth == "Depth (m)"
    assert config.columns.output.convg == "convg. (-)"


def test_default_parameters():
    config = Configurator()

    assert config.parameters.area_ratio == 0.80
    assert config.parameters.gamma_soil is None


def test_default_cleansing():
    config = Configurator()

    assert config.cleansing.start_depth is None
    assert config.cleansing.spacing is None

    assert config.cleansing.indicators == []
    assert config.cleansing.clean_mode == "replace"
