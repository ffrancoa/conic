from textwrap import dedent

import pytest
from pydantic import ValidationError

from conic import Processor


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
    
    p = Processor.from_toml(toml_path)
    
    assert p.parameters.gamma_water == 9.99
    assert p.cleansing.clean_mode == "remove"

def test_validate_from_toml(tmp_path):
    toml_content = dedent("""
        [parameters]
        area_ratio = 1.05
    """)
    
    toml_path = tmp_path / "conic.toml"
    toml_path.write_text(toml_content)
    
    with pytest.raises(ValidationError):
        _ = Processor.from_toml(toml_path)
