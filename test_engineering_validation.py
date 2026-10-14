
import pytest

from problem_solver import solve_question

from calculations import (
    hydrostatic_pressure,
    equivalent_circulating_density,
    api_gravity,
    annular_velocity,
    pipe_velocity,
    annular_capacity,


)


def test_hydrostatic_pressure_reference_example():
    # Reference example:
    # 12 ppg mud, 12,500 ft TVD = 7,800 psi
    result = hydrostatic_pressure(12, 12500)

    assert result == pytest.approx(7800.0)


def test_ecd_independent_benchmark():
    # ECD = MW + pressure loss / (0.052 * TVD)
    # 10 + 500 / (0.052 * 10,000)
    expected = 10 + 500 / (0.052 * 10000)

    result = equivalent_circulating_density(
        10,   # Mud weight, ppg
        500,  # Annular pressure loss, psi
        10000 # True vertical depth, ft
    )

    assert result == pytest.approx(expected)


def test_api_gravity_independent_benchmark():
    # API gravity = (141.5 / specific gravity) - 131.5
    # Specific gravity = 0.85
    expected = (141.5 / 0.85) - 131.5

    result = api_gravity(0.85)

    assert result == pytest.approx(expected)


def test_api_gravity_rejects_zero_specific_gravity():
    with pytest.raises(ValueError):
        api_gravity(0)


def test_api_gravity_rejects_negative_specific_gravity():
    with pytest.raises(ValueError):
        api_gravity(-0.85)
 
 
 
def test_annular_velocity_benchmark():
    # 24.51 * flow rate / (hole diameter² - pipe OD²)
    # Inputs: 500 gpm, 8.5-inch hole, 5-inch pipe
    expected = 259.3650793650794

    result = annular_velocity(500, 8.5, 5)

    assert result == pytest.approx(expected)


def test_pipe_velocity_benchmark():
    # 24.51 * flow rate / pipe ID²
    # Inputs: 500 gpm, 4-inch pipe ID
    expected = 765.9375

    result = pipe_velocity(500, 4)

    assert result == pytest.approx(expected)


def test_annular_capacity_benchmark():
    # (hole diameter² - pipe OD²) / 1029.4
    # Inputs: 8.5-inch hole, 5-inch pipe
    expected = 47.25 / 1029.4

    result = annular_capacity(8.5, 5)

    assert result == pytest.approx(expected)


def test_required_mud_weight_question_solver():
    result = solve_question(
        "Calculate required mud weight for "
        "formation pressure 4000 psi at depth 5000 ft"
    )

    assert result["success"] is True
    assert result["calculation"] == "Required Mud Weight"
    assert result["answer"] == pytest.approx(15.3846, abs=0.0001)
    assert result["unit"] == "ppg"
