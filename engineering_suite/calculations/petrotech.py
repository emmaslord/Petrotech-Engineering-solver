
import math


# ==========================================
# 1. PRESSURE AND MUD WEIGHT CALCULATIONS
# ==========================================

def hydrostatic_pressure(mud_weight_ppg: float, tvd_ft: float) -> float:
    """Calculate hydrostatic pressure in psi."""
    if mud_weight_ppg <= 0 or tvd_ft <= 0:
        raise ValueError("Mud weight and TVD must be positive.")

    return 0.052 * mud_weight_ppg * tvd_ft


def formation_pressure(gradient_psi_ft: float, tvd_ft: float) -> float:
    """Estimate formation pressure in psi."""
    if gradient_psi_ft < 0 or tvd_ft < 0:
        raise ValueError("Gradient and TVD cannot be negative.")

    return gradient_psi_ft * tvd_ft


def required_mud_weight(pressure_psi: float, tvd_ft: float) -> float:
    """Calculate mud weight corresponding to a target pressure."""
    if pressure_psi < 0 or tvd_ft <= 0:
        raise ValueError("Pressure must be non-negative and TVD positive.")

    return pressure_psi / (0.052 * tvd_ft)


def equivalent_circulating_density(
    mud_weight_ppg: float,
    annular_pressure_loss_psi: float,
    tvd_ft: float,
) -> float:
    """Estimate ECD in ppg using annular friction pressure loss."""
    if mud_weight_ppg <= 0:
        raise ValueError("Mud weight must be positive.")
    if annular_pressure_loss_psi < 0:
        raise ValueError("Annular pressure loss cannot be negative.")
    if tvd_ft <= 0:
        raise ValueError("TVD must be positive.")

    return mud_weight_ppg + (
        annular_pressure_loss_psi / (0.052 * tvd_ft)
    )


# ==========================================
# 2. FLUID PROPERTY CONVERSIONS
# ==========================================

def api_gravity(specific_gravity: float) -> float:
    """Convert specific gravity to API gravity."""
    if specific_gravity <= 0:
        raise ValueError("Specific gravity must be positive.")

    return 141.5 / specific_gravity - 131.5


def specific_gravity(api: float) -> float:
    """Convert API gravity to specific gravity."""
    if api <= -131.5:
        raise ValueError("API gravity must be greater than -131.5.")

    return 141.5 / (api + 131.5)


# ==========================================
# 3. RESERVOIR VOLUME ESTIMATES
# ==========================================

def ooip(
    area_acres: float,
    net_pay_ft: float,
    porosity: float,
    water_saturation: float,
    boi_rb_stb: float,
) -> float:
    """Estimate original oil in place in stock-tank barrels."""
    if area_acres <= 0 or net_pay_ft <= 0 or boi_rb_stb <= 0:
        raise ValueError("Area, net pay and Boi must be positive.")

    if not 0 <= porosity <= 1:
        raise ValueError("Porosity must be between 0 and 1.")

    if not 0 <= water_saturation <= 1:
        raise ValueError("Water saturation must be between 0 and 1.")

    return (
        7758
        * area_acres
        * net_pay_ft
        * porosity
        * (1 - water_saturation)
        / boi_rb_stb
    )


def ogip(
    area_acres: float,
    net_pay_ft: float,
    porosity: float,
    water_saturation: float,
    bgi_res_ft3_scf: float,
) -> float:
    """Estimate original gas in place in standard cubic feet."""
    if area_acres <= 0 or net_pay_ft <= 0 or bgi_res_ft3_scf <= 0:
        raise ValueError("Area, net pay and Bgi must be positive.")

    if not 0 <= porosity <= 1:
        raise ValueError("Porosity must be between 0 and 1.")

    if not 0 <= water_saturation <= 1:
        raise ValueError("Water saturation must be between 0 and 1.")

    return (
        43560
        * area_acres
        * net_pay_ft
        * porosity
        * (1 - water_saturation)
        / bgi_res_ft3_scf
    )


# ==========================================
# 4. DRILL PIPE AND ANNULAR VELOCITIES
# ==========================================

def annular_velocity(
    flow_rate_gpm: float,
    hole_diameter_in: float,
    pipe_od_in: float,
) -> float:
    """Calculate average annular velocity in ft/min."""
    if flow_rate_gpm <= 0:
        raise ValueError("Flow rate must be positive.")
    if hole_diameter_in <= 0 or pipe_od_in <= 0:
        raise ValueError("Diameters must be positive.")
    if hole_diameter_in <= pipe_od_in:
        raise ValueError("Hole diameter must be greater than pipe OD.")

    return 24.51 * flow_rate_gpm / (
        hole_diameter_in**2 - pipe_od_in**2
    )


def pipe_velocity(
    flow_rate_gpm: float,
    pipe_id_in: float,
) -> float:
    """Calculate average internal pipe velocity in ft/min."""
    if flow_rate_gpm <= 0:
        raise ValueError("Flow rate must be positive.")
    if pipe_id_in <= 0:
        raise ValueError("Pipe inside diameter must be positive.")

    return 24.51 * flow_rate_gpm / pipe_id_in**2


# ==========================================
# 5. TRIPLEX MUD PUMP
# ==========================================

def triplex_pump_output(
    liner_diameter_in: float,
    stroke_length_in: float,
    strokes_per_min: float,
    volumetric_efficiency: float = 0.90,
) -> float:
    """Estimate triplex pump output in US gallons per minute."""
    if liner_diameter_in <= 0:
        raise ValueError("Liner diameter must be positive.")
    if stroke_length_in <= 0:
        raise ValueError("Stroke length must be positive.")
    if strokes_per_min <= 0:
        raise ValueError("Strokes per minute must be positive.")
    if not 0 < volumetric_efficiency <= 1:
        raise ValueError(
            "Volumetric efficiency must be greater than 0 and at most 1."
        )

    displacement_in3_per_min = (
        3
        * math.pi / 4
        * liner_diameter_in**2
        * stroke_length_in
        * strokes_per_min
    )

    return displacement_in3_per_min * 0.004329 * volumetric_efficiency


# ==========================================
# 6. HOLE, PIPE AND ANNULAR CAPACITIES
# ==========================================

def hole_capacity(hole_diameter_in: float) -> float:
    """Calculate hole capacity in barrels per foot."""
    if hole_diameter_in <= 0:
        raise ValueError("Hole diameter must be positive.")

    return hole_diameter_in**2 / 1029.4


def pipe_capacity(pipe_id_in: float) -> float:
    """Calculate internal pipe capacity in barrels per foot."""
    if pipe_id_in <= 0:
        raise ValueError("Pipe inside diameter must be positive.")

    return pipe_id_in**2 / 1029.4


def annular_capacity(
    hole_diameter_in: float,
    pipe_od_in: float,
) -> float:
    """Calculate annular capacity in barrels per foot."""
    if hole_diameter_in <= 0 or pipe_od_in <= 0:
        raise ValueError("Diameters must be positive.")

    if hole_diameter_in <= pipe_od_in:
        raise ValueError("Hole diameter must be greater than pipe OD.")

    return (
        hole_diameter_in**2 - pipe_od_in**2
    ) / 1029.4


# ==========================================
# 7. WELLBORE AND ANNULAR VOLUMES
# ==========================================

def wellbore_volume(
    hole_diameter_in: float,
    length_ft: float,
) -> float:
    """Calculate wellbore volume in barrels."""
    if length_ft <= 0:
        raise ValueError("Length must be positive.")

    return hole_capacity(hole_diameter_in) * length_ft


def annular_volume(
    hole_diameter_in: float,
    pipe_od_in: float,
    length_ft: float,
) -> float:
    """Calculate annular volume in barrels."""
    if length_ft <= 0:
        raise ValueError("Length must be positive.")

    return annular_capacity(
        hole_diameter_in, pipe_od_in
    ) * length_ft


# ==========================================
# 8. CIRCULATION TIME
# ==========================================

def bottoms_up_time(
    annular_capacity_bbl_ft: float,
    annular_length_ft: float,
    flow_rate_bbl_min: float,
) -> float:
    """Estimate bottoms-up circulation time in minutes."""
    if annular_capacity_bbl_ft <= 0:
        raise ValueError("Annular capacity must be positive.")
    if annular_length_ft <= 0:
        raise ValueError("Annular length must be positive.")
    if flow_rate_bbl_min <= 0:
        raise ValueError("Flow rate must be positive.")

    return (
        annular_capacity_bbl_ft * annular_length_ft
    ) / flow_rate_bbl_min
