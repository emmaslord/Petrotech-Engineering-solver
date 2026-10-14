
from engineering_calculations import (
    hydrostatic_pressure,
    force,
    pressure,
    ohms_law,
    rectangle_area,
    circle_area,
    kinetic_energy,
    electrical_power,
    density,
)

assert hydrostatic_pressure(1000, 10) == 98100
assert force(10, 2) == 20
assert pressure(100, 2) == 50
assert ohms_law(voltage=None, current=2, resistance=5) == 10
assert rectangle_area(5, 4) == 20
assert round(circle_area(2), 4) == 12.5664
assert kinetic_energy(2, 3) == 9
assert electrical_power(12, 2) == 24
assert density(100, 5) == 20

print("All 9 engineering calculation tests passed!")
