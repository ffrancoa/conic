import dataclasses

from conic.config import Configurator


def test_round_trip_defaults():
    config = Configurator()

    assert Configurator.from_dict(dataclasses.asdict(config)) == config


def test_round_trip_custom_values():
    config = Configurator.from_dict(
        {
            "parameters": {"gamma_soil": 19.5, "water_level": 1.2, "rolling": 3},
            "cleansing": {"indicators": [-9999.0], "max_sleeve_offset": 3},
            "settings": {"p_ref": 100.0, "tolerance": 1e-6},
            "columns": {
                "input": {"u2": "u (kPa)"},
                "correlation": {"bi14": {"fc": "FC (%)"}},
            },
        }
    )

    assert Configurator.from_dict(dataclasses.asdict(config)) == config
