import polars as pl
import pytest
from polars.exceptions import ColumnNotFoundError

from conic.calculate.calibrate import CalibrationResult, calibrate_bi14
from conic.calculate.calibrate._boulanger2014 import INTERCEPT, SLOPE

COL_IC = "Ic"
COL_FC = "F%"


def _pairs(ic, fc):
    return pl.LazyFrame(
        {COL_IC: ic, COL_FC: fc},
        schema_overrides={COL_IC: pl.Float64, COL_FC: pl.Float64},
    )


def _synthesize_fc(ic, coefficient):
    return [SLOPE * (value + coefficient) - INTERCEPT for value in ic]


def test_exact_recovery():
    ic = [1.5, 2.0, 2.5, 3.0]
    coefficient = -0.518
    fc = _synthesize_fc(ic, coefficient)

    result = calibrate_bi14(_pairs(ic, fc), COL_IC, COL_FC)

    assert isinstance(result, CalibrationResult)
    assert result.coefficient == pytest.approx(coefficient)
    assert result.residual_std == pytest.approx(0.0, abs=1e-12)
    assert result.n_points == 4


def test_residual_std_positive_with_scatter():
    ic = [1.5, 2.0, 2.5, 3.0]
    fc = _synthesize_fc(ic, -0.5)
    fc[0] += 8.0
    fc[3] -= 8.0

    result = calibrate_bi14(_pairs(ic, fc), COL_IC, COL_FC)

    assert result.residual_std > 0.0
    assert result.n_points == 4


def test_hand_computed_case():
    # response = Ic - FC/80; mean/std over the two valid pairs.
    # pair A: Ic=2.0, FC=23  -> response = 2.0 - 0.2875 = 1.7125
    # pair B: Ic=3.0, FC=103 -> response = 3.0 - 1.2875 = 1.7125
    result = calibrate_bi14(_pairs([2.0, 3.0], [23.0, 103.0]), COL_IC, COL_FC)

    expected_coefficient = -1.7125 + INTERCEPT / SLOPE
    assert result.coefficient == pytest.approx(expected_coefficient)
    assert result.residual_std == pytest.approx(0.0, abs=1e-12)


def test_drops_missing_pairs():
    ic = [1.5, 2.0, float("nan"), 2.5, None]
    fc = _synthesize_fc([1.5, 2.0, 0.0, 2.5, 0.0], -0.3)
    fc[2] = float("nan")
    fc[4] = None

    result = calibrate_bi14(_pairs(ic, fc), COL_IC, COL_FC)

    assert result.n_points == 3
    assert result.coefficient == pytest.approx(-0.3)


def test_insufficient_data_raises():
    with pytest.raises(ValueError):
        calibrate_bi14(_pairs([2.0], [23.0]), COL_IC, COL_FC)


def test_missing_column_raises():
    with pytest.raises(ColumnNotFoundError):
        calibrate_bi14(pl.LazyFrame({COL_IC: [2.0, 3.0]}), COL_IC, COL_FC)


def test_len_returns_n_points():
    ic = [1.5, 2.0, 2.5]
    fc = _synthesize_fc(ic, -0.4)

    result = calibrate_bi14(_pairs(ic, fc), COL_IC, COL_FC)

    assert len(result) == result.n_points == 3
