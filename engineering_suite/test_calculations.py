
import unittest
import sys
from pathlib import Path

# Add the directory containing the calculations package when running this
# test from its nested location. This path is injected at runtime, so
# Pyright cannot resolve the package without a local configuration override.
for directory in Path(__file__).resolve().parents:
    if (directory / "calculations").is_dir():
        sys.path.insert(0, str(directory))
        break

# pyright: reportMissingImports=false
from calculations.petroleum import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_density,
    api_gravity,
    annular_velocity,
    pipe_velocity,
)
from calculations.mechanical import force, kinetic_energy, density
from calculations.electrical import electrical_power, ohms_law
from calculations.civil import rectangle_area, circle_area
from calculations.general import percentage, unit_weight


class TestEngineeringCalculations(unittest.TestCase):

    def test_hydrostatic_pressure(self):
        self.assertAlmostEqual(hydrostatic_pressure(1000, 10), 98100)

    def test_formation_pressure(self):
        self.assertAlmostEqual(formation_pressure(10000, 10), 100000)

    def test_required_mud_density(self):
        self.assertAlmostEqual(required_mud_density(98100, 10), 1000)

    def test_api_gravity(self):
        self.assertAlmostEqual(api_gravity(1.0), 10.0)

    def test_force(self):
        self.assertEqual(force(10, 2), 20)

    def test_kinetic_energy(self):
        self.assertEqual(kinetic_energy(10, 2), 20)

    def test_density(self):
        self.assertEqual(density(100, 5), 20)

    def test_electrical_power(self):
        self.assertEqual(electrical_power(12, 2), 24)

    def test_ohms_law(self):
        self.assertEqual(ohms_law(voltage=12, resistance=4)["current"], 3)

    def test_rectangle_area(self):
        self.assertEqual(rectangle_area(5, 4), 20)

    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(1), 3.141592653589793)

    def test_percentage(self):
        self.assertEqual(percentage(25, 100), 25)

    def test_unit_weight(self):
        self.assertAlmostEqual(unit_weight(1000), 9810)

    def test_pipe_velocity(self):
        self.assertAlmostEqual(pipe_velocity(0.01, 0.1), 1.2732395447)

    def test_annular_velocity(self):
        self.assertGreater(annular_velocity(0.01, 0.2, 0.1), 0)


if __name__ == "__main__":
    unittest.main()
