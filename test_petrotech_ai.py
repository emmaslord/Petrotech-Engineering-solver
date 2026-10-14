
"""Automated tests for the PetroTech AI Core."""

import unittest

from petrotech_ai.tools import (
    calculate_hydrostatic_pressure,
    calculate_formation_pressure,
    calculate_required_mud_weight,
    calculate_api_gravity,
)
from petrotech_ai.assistant import answer_question


class TestPetroTechAITools(unittest.TestCase):

    def test_hydrostatic_pressure(self):
        result = calculate_hydrostatic_pressure(10, 5000)
        self.assertAlmostEqual(result["pressure_psi"], 2600)

    def test_formation_pressure(self):
        result = calculate_formation_pressure(0.465, 5000)
        self.assertAlmostEqual(result["pressure_psi"], 2325)

    def test_required_mud_weight(self):
        result = calculate_required_mud_weight(2600, 5000)
        self.assertAlmostEqual(result["mud_weight_ppg"], 10)

    def test_api_gravity(self):
        result = calculate_api_gravity(0.85)
        self.assertAlmostEqual(result["api_gravity"], 34.970588, places=5)

    def test_invalid_mud_weight(self):
        with self.assertRaises(ValueError):
            calculate_hydrostatic_pressure(-1, 5000)

    def test_assistant_hydrostatic_question(self):
        result = answer_question(
            "Calculate hydrostatic pressure for mud weight 10 ppg and TVD 5000 ft."
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "verified_engineering_tool")
        self.assertAlmostEqual(result["pressure_psi"], 2600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
