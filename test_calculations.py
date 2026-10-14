
import pytest

from calculations import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_weight,
    api_gravity,
    specific_gravity,
    ooip,
    ogip,
)


def test_hydrostatic_pressure():
    assert hydrostatic_pressure(10, 5000) == 2600


def test_formation_pressure():
    assert formation_pressure(0.465, 5000) == 2325


def test_required_mud_weight():
    assert required_mud_weight(2600, 5000) == 10


def test_api_gravity_round_trip():
    sg = 0.85
    assert specific_gravity(api_gravity(sg)) == pytest.approx(sg)



def test_ooip():
    result = ooip(640, 50, 0.20, 0.30, 1.20)
    assert result == pytest.approx(28_963_200)

def test_ogip():
    result = ogip(640, 50, 0.20, 0.30, 0.005)
    assert result == pytest.approx(39_029_760_000)


def test_invalid_depth():
    with pytest.raises(ValueError):
        hydrostatic_pressure(10, 0)



# Additional hydrostatic pressure reference cases

def test_hydrostatic_reference_case_2():
    # Reference example: 12 ppg at 12,500 ft = 7,800 psi
    assert hydrostatic_pressure(12, 12500) == 7800


def test_hydrostatic_pressure_scales_with_depth():
    shallow = hydrostatic_pressure(10, 1000)
    deep = hydrostatic_pressure(10, 2000)
    assert deep == pytest.approx(2 * shallow)


# API gravity reference and input validation

def test_api_gravity_for_sg_085():
    assert api_gravity(0.85) == pytest.approx(34.9705882353)


def test_specific_gravity_for_api_35():
    assert specific_gravity(35) == pytest.approx(141.5 / 166.5)


def test_api_gravity_rejects_zero_sg():
    with pytest.raises(ValueError):
        api_gravity(0)


def test_specific_gravity_rejects_invalid_api():
    with pytest.raises(ValueError):
        specific_gravity(-131.5)



from calculations import annular_velocity


def test_annular_velocity():
    result = annular_velocity(300, 8.5, 5)
    assert abs(result - 155.62) < 0.02

def test_annular_velocity_rejects_hole_smaller_than_pipe():
    import pytest

    with pytest.raises(ValueError):
        annular_velocity(300, 4, 5)


def test_annular_velocity_rejects_zero_flow():
    import pytest

    with pytest.raises(ValueError):
        annular_velocity(0, 8.5, 5)


from calculations import pipe_velocity


def test_pipe_velocity():
    result = pipe_velocity(300, 4)
    assert abs(result - 459.56) < 0.02


def test_pipe_velocity_rejects_zero_flow():
    import pytest

    with pytest.raises(ValueError):
        pipe_velocity(0, 4)


def test_pipe_velocity_rejects_zero_diameter():
    import pytest

    with pytest.raises(ValueError):
        pipe_velocity(300, 0)



from calculations import triplex_pump_output


def test_triplex_pump_output():
    result = triplex_pump_output(6, 12, 60, 0.90)
    assert abs(result - 237.94) < 0.5


def test_triplex_pump_output_rejects_zero_liner():
    import pytest

    with pytest.raises(ValueError):
        triplex_pump_output(0, 12, 60, 0.90)


def test_triplex_pump_output_rejects_invalid_efficiency():
    import pytest

    with pytest.raises(ValueError):
        triplex_pump_output(6, 12, 60, 1.1)


from calculations import equivalent_circulating_density


def test_equivalent_circulating_density():
    result = equivalent_circulating_density(10, 300, 5000)
    assert abs(result - 11.1538) < 0.01


def test_ecd_rejects_zero_tvd():
    import pytest

    with pytest.raises(ValueError):
        equivalent_circulating_density(10, 300, 0)


def test_ecd_rejects_negative_pressure_loss():
    import pytest

    with pytest.raises(ValueError):
        equivalent_circulating_density(10, -10, 5000)

from calculations import annular_capacity

def test_annular_capacity():
    result = annular_capacity(8.5, 5.0)
    assert abs(result - 0.0459) < 0.0001

def test_annular_capacity_rejects_invalid_diameters():
    import pytest
    with pytest.raises(ValueError):
        annular_capacity(5.0, 8.5)
        
        
from calculations import bottoms_up_time

def test_bottoms_up_time():
    result = bottoms_up_time(0.0459, 5000, 10)
    assert abs(result - 22.95) < 0.01

def test_bottoms_up_time_rejects_zero_flow():
    import pytest
    with pytest.raises(ValueError):
        bottoms_up_time(0.0459, 5000, 0)

def test_bottoms_up_time_rejects_negative_length():
    import pytest
    with pytest.raises(ValueError):
        bottoms_up_time(0.0459, -5000, 10)


import pytest

from calculations import pipe_capacity, hole_capacity


def test_pipe_capacity():
    assert abs(pipe_capacity(4.0) - (16 / 1029.4)) < 1e-9


def test_pipe_capacity_rejects_zero_diameter():
    with pytest.raises(ValueError):
        pipe_capacity(0)


def test_hole_capacity():
    assert abs(hole_capacity(8.5) - (8.5**2 / 1029.4)) < 1e-9


def test_hole_capacity_rejects_negative_diameter():
    with pytest.raises(ValueError):
        hole_capacity(-8.5)


from calculations import wellbore_volume


def test_wellbore_volume():
    assert abs(
        wellbore_volume(8.5, 1000)
        - ((8.5**2 / 1029.4) * 1000)
    ) < 1e-9


def test_wellbore_volume_rejects_zero_length():
    with pytest.raises(ValueError):
        wellbore_volume(8.5, 0)
