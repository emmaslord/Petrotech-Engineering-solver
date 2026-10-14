
"""Verified engineering tools for PetroTech AI."""

from calculations import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_weight,
    api_gravity,
)


def calculate_hydrostatic_pressure(
    mud_weight_ppg: float,
    tvd_ft: float,
) -> dict:
    """Calculate hydrostatic pressure in psi."""
    if not 0 < mud_weight_ppg <= 30:
        raise ValueError("Mud weight must be greater than 0 and at most 30 ppg.")
    if not 0 < tvd_ft <= 100000:
        raise ValueError("TVD must be greater than 0 and at most 100,000 ft.")

    pressure = hydrostatic_pressure(mud_weight_ppg, tvd_ft)

    return {
        "calculation": "Hydrostatic Pressure",
        "mud_weight_ppg": mud_weight_ppg,
        "tvd_ft": tvd_ft,
        "pressure_psi": pressure,
        "unit": "psi",
        "formula": "0.052 × mud weight (ppg) × TVD (ft)",
    }


def calculate_formation_pressure(
    gradient_psi_ft: float,
    tvd_ft: float,
) -> dict:
    """Calculate formation pressure from a supplied pressure gradient."""
    if not 0 < gradient_psi_ft <= 2:
        raise ValueError("Gradient must be greater than 0 and at most 2 psi/ft.")
    if not 0 < tvd_ft <= 100000:
        raise ValueError("TVD must be greater than 0 and at most 100,000 ft.")

    pressure = formation_pressure(gradient_psi_ft, tvd_ft)

    return {
        "calculation": "Formation Pressure",
        "gradient_psi_ft": gradient_psi_ft,
        "tvd_ft": tvd_ft,
        "pressure_psi": pressure,
        "unit": "psi",
        "formula": "Pressure gradient (psi/ft) × TVD (ft)",
    }


def calculate_required_mud_weight(
    pressure_psi: float,
    tvd_ft: float,
) -> dict:
    """Calculate mud weight required for a supplied pressure and TVD."""
    if pressure_psi <= 0:
        raise ValueError("Pressure must be greater than 0 psi.")
    if not 0 < tvd_ft <= 100000:
        raise ValueError("TVD must be greater than 0 and at most 100,000 ft.")

    mud_weight = required_mud_weight(pressure_psi, tvd_ft)

    return {
        "calculation": "Required Mud Weight",
        "pressure_psi": pressure_psi,
        "tvd_ft": tvd_ft,
        "mud_weight_ppg": mud_weight,
        "unit": "ppg",
        "formula": "Required mud weight = pressure ÷ (0.052 × TVD)",
    }


def calculate_api_gravity(specific_gravity: float) -> dict:
    """Convert specific gravity to API gravity."""
    if not 0 < specific_gravity <= 3:
        raise ValueError("Specific gravity must be greater than 0 and at most 3.")

    gravity = api_gravity(specific_gravity)

    return {
        "calculation": "API Gravity",
        "specific_gravity": specific_gravity,
        "api_gravity": gravity,
        "unit": "°API",
        "formula": "API gravity = (141.5 ÷ specific gravity) − 131.5",
    }
