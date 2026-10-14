
import math


def hydrostatic_pressure(mud_density, true_vertical_depth):
    """Calculate hydrostatic pressure in Pa."""
    if mud_density <= 0:
        raise ValueError("Fluid density must be greater than zero.")
    if true_vertical_depth < 0:
        raise ValueError("Depth cannot be negative.")

    return mud_density * 9.81 * true_vertical_depth


def force(mass, acceleration):
    """Calculate force using Newton's second law."""
    if mass < 0:
        raise ValueError("Mass cannot be negative.")

    return mass * acceleration


def pressure(force_value, area):
    """Calculate pressure in Pa."""
    if area <= 0:
        raise ValueError("Area must be greater than zero.")

    return force_value / area


def ohms_law(voltage=None, current=None, resistance=None):
    """Calculate one missing Ohm's law quantity."""
    if voltage is None:
        if current is None or resistance is None:
            raise ValueError("Provide current and resistance.")
        if resistance < 0:
            raise ValueError("Resistance cannot be negative.")
        return current * resistance

    if current is None:
        if resistance is None:
            raise ValueError("Provide voltage and resistance.")
        if resistance <= 0:
            raise ValueError("Resistance must be greater than zero.")
        return voltage / resistance

    if resistance is None:
        if current == 0:
            raise ValueError("Current cannot be zero to calculate resistance.")
        return voltage / current

    raise ValueError("Leave exactly one quantity blank.")


def rectangle_area(length, width):
    """Calculate the area of a rectangle in square metres."""
    if length < 0 or width < 0:
        raise ValueError("Length and width cannot be negative.")

    return length * width


def circle_area(radius):
    """Calculate the area of a circle in square metres."""
    if radius < 0:
        raise ValueError("Radius cannot be negative.")

    return math.pi * radius ** 2


def kinetic_energy(mass, velocity):
    """Calculate kinetic energy in joules."""
    if mass < 0:
        raise ValueError("Mass cannot be negative.")

    return 0.5 * mass * velocity ** 2


def electrical_power(voltage, current):
    """Calculate electrical power in watts."""
    return voltage * current


def density(mass, volume):
    """Calculate density in kg/m³."""
    if mass < 0:
        raise ValueError("Mass cannot be negative.")
    if volume <= 0:
        raise ValueError("Volume must be greater than zero.")

    return mass / volume
