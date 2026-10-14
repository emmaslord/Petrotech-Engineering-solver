
import math


def rectangle_area(length, width):
    """Rectangle area in square units."""
    if length < 0 or width < 0:
        raise ValueError("Dimensions cannot be negative.")
    return length * width


def circle_area(radius):
    """Circle area in square units."""
    if radius < 0:
        raise ValueError("Radius cannot be negative.")
    return math.pi * radius**2
