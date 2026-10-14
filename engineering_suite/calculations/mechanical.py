
def force(mass, acceleration):
    """Force in newtons."""
    if mass < 0:
        raise ValueError("Mass cannot be negative.")
    return mass * acceleration


def pressure(force_value, area):
    """Pressure magnitude in pascals."""
    if force_value < 0 or area <= 0:
        raise ValueError("Force must be non-negative and area positive.")
    return force_value / area


def kinetic_energy(mass, velocity):
    """Kinetic energy in joules."""
    if mass < 0:
        raise ValueError("Mass cannot be negative.")
    return 0.5 * mass * velocity**2


def density(mass, volume):
    """Density in kg/m³ for mass in kg and volume in m³."""
    if mass < 0 or volume <= 0:
        raise ValueError("Mass must be non-negative and volume positive.")
    return mass / volume
