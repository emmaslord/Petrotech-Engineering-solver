
def hydrostatic_pressure(mud_density, true_vertical_depth):
    """Pressure in Pa; density in kg/m³ and depth in m."""
    if mud_density <= 0 or true_vertical_depth < 0:
        raise ValueError("Density must be positive and depth non-negative.")
    return mud_density * 9.81 * true_vertical_depth


def formation_pressure(pressure_gradient, true_vertical_depth):
    """Pressure in Pa; gradient in Pa/m and depth in m."""
    if pressure_gradient < 0 or true_vertical_depth < 0:
        raise ValueError("Gradient and depth cannot be negative.")
    return pressure_gradient * true_vertical_depth


def required_mud_density(formation_pressure_value, depth):
    """Ideal density in kg/m³ to balance a pressure at a given depth."""
    if formation_pressure_value < 0 or depth <= 0:
        raise ValueError("Pressure must be non-negative and depth positive.")
    return formation_pressure_value / (9.81 * depth)


def equivalent_circulating_density(
    mud_density, annular_pressure_loss, true_vertical_depth
):
    """Simplified ECD in kg/m³."""
    if mud_density <= 0 or annular_pressure_loss < 0:
        raise ValueError("Density must be positive and pressure loss non-negative.")
    if true_vertical_depth <= 0:
        raise ValueError("Depth must be positive.")
    return mud_density + annular_pressure_loss / (
        9.81 * true_vertical_depth
    )


def api_gravity(specific_gravity):
    """API gravity in degrees API."""
    if specific_gravity <= 0:
        raise ValueError("Specific gravity must be positive.")
    return 141.5 / specific_gravity - 131.5


def specific_gravity_from_api(api_value):
    """Specific gravity corresponding to API gravity."""
    if api_value <= -131.5:
        raise ValueError("API gravity must be greater than -131.5.")
    return 141.5 / (api_value + 131.5)


def annular_velocity(flow_rate, hole_diameter, pipe_outer_diameter):
    """Average annular velocity in m/s; flow in m³/s, diameters in m."""
    if flow_rate < 0:
        raise ValueError("Flow rate cannot be negative.")
    if hole_diameter <= pipe_outer_diameter or pipe_outer_diameter < 0:
        raise ValueError("Hole diameter must exceed pipe diameter.")

    area = 3.141592653589793 / 4 * (
        hole_diameter**2 - pipe_outer_diameter**2
    )
    return flow_rate / area


def pipe_velocity(flow_rate, pipe_inner_diameter):
    """Average internal velocity in m/s."""
    if flow_rate < 0 or pipe_inner_diameter <= 0:
        raise ValueError("Flow must be non-negative and diameter positive.")

    area = 3.141592653589793 / 4 * pipe_inner_diameter**2
    return flow_rate / area


def triplex_pump_output(
    liner_diameter, stroke_length, strokes_per_minute, efficiency=1.0
):
    """Idealized triplex output in m³/min, adjusted by efficiency."""
    if liner_diameter <= 0 or stroke_length < 0:
        raise ValueError("Liner diameter must be positive; stroke non-negative.")
    if strokes_per_minute < 0 or not 0 < efficiency <= 1:
        raise ValueError("Check stroke rate and efficiency (0, 1].")

    displacement_per_stroke = (
        3 * 3.141592653589793 / 4
        * liner_diameter**2
        * stroke_length
    )
    return displacement_per_stroke * strokes_per_minute * efficiency
