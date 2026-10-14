
from flask import Blueprint, request, jsonify
from calculations import petrotech

petrotech_api = Blueprint("petrotech_api", __name__)


PETROTECH_CALCULATIONS = {
    "petrotech_hydrostatic_pressure": {
        "label": "PetroTech Hydrostatic Pressure",
        "fields": ["mud_weight_ppg", "tvd_ft"],
        "units": ["ppg", "ft"],
        "function": petrotech.hydrostatic_pressure,
    },
    "petrotech_formation_pressure": {
        "label": "PetroTech Formation Pressure",
        "fields": ["gradient_psi_ft", "tvd_ft"],
        "units": ["psi/ft", "ft"],
        "function": petrotech.formation_pressure,
    },
    "petrotech_required_mud_weight": {
        "label": "PetroTech Required Mud Weight",
        "fields": ["pressure_psi", "tvd_ft"],
        "units": ["psi", "ft"],
        "function": petrotech.required_mud_weight,
    },
    "petrotech_ecd": {
        "label": "PetroTech Equivalent Circulating Density",
        "fields": [
            "mud_weight_ppg",
            "annular_pressure_loss_psi",
            "tvd_ft",
        ],
        "units": ["ppg", "psi", "ft"],
        "function": petrotech.equivalent_circulating_density,
    },
    "petrotech_api_gravity": {
        "label": "PetroTech API Gravity",
        "fields": ["specific_gravity"],
        "units": [""],
        "function": petrotech.api_gravity,
    },
    "petrotech_specific_gravity": {
        "label": "PetroTech Specific Gravity",
        "fields": ["api"],
        "units": ["°API"],
        "function": petrotech.specific_gravity,
    },
    "petrotech_ooip": {
        "label": "Original Oil Initially In Place",
        "fields": [
            "area_acres",
            "net_pay_ft",
            "porosity",
            "water_saturation",
            "boi_rb_stb",
        ],
        "units": ["acres", "ft", "fraction", "fraction", "rb/stb"],
        "function": petrotech.ooip,
    },
    "petrotech_ogip": {
        "label": "Original Gas Initially In Place",
        "fields": [
            "area_acres",
            "net_pay_ft",
            "porosity",
            "water_saturation",
            "bgi_res_ft3_scf",
        ],
        "units": ["acres", "ft", "fraction", "fraction", "res ft³/scf"],
        "function": petrotech.ogip,
    },
    "petrotech_annular_velocity": {
        "label": "PetroTech Annular Velocity",
        "fields": ["flow_rate_gpm", "hole_diameter_in", "pipe_od_in"],
        "units": ["US gpm", "in", "in"],
        "function": petrotech.annular_velocity,
    },
    "petrotech_pipe_velocity": {
        "label": "PetroTech Pipe Velocity",
        "fields": ["flow_rate_gpm", "pipe_id_in"],
        "units": ["US gpm", "in"],
        "function": petrotech.pipe_velocity,
    },
    "petrotech_triplex_pump_output": {
        "label": "Triplex Pump Output",
        "fields": [
            "liner_diameter_in",
            "stroke_length_in",
            "strokes_per_min",
            "volumetric_efficiency",
        ],
        "units": ["in", "in", "strokes/min", "fraction"],
        "function": petrotech.triplex_pump_output,
    },
    "petrotech_hole_capacity": {
        "label": "Hole Capacity",
        "fields": ["hole_diameter_in"],
        "units": ["in"],
        "function": petrotech.hole_capacity,
    },
    "petrotech_pipe_capacity": {
        "label": "Pipe Capacity",
        "fields": ["pipe_id_in"],
        "units": ["in"],
        "function": petrotech.pipe_capacity,
    },
    "petrotech_annular_capacity": {
        "label": "Annular Capacity",
        "fields": ["hole_diameter_in", "pipe_od_in"],
        "units": ["in", "in"],
        "function": petrotech.annular_capacity,
    },
    "petrotech_wellbore_volume": {
        "label": "Wellbore Volume",
        "fields": ["hole_diameter_in", "length_ft"],
        "units": ["in", "ft"],
        "function": petrotech.wellbore_volume,
    },
    "petrotech_annular_volume": {
        "label": "Annular Volume",
        "fields": ["hole_diameter_in", "pipe_od_in", "length_ft"],
        "units": ["in", "in", "ft"],
        "function": petrotech.annular_volume,
    },
    "petrotech_bottoms_up_time": {
        "label": "Bottoms-Up Circulation Time",
        "fields": [
            "annular_capacity_bbl_ft",
            "annular_length_ft",
            "flow_rate_bbl_min",
        ],
        "units": ["bbl/ft", "ft", "bbl/min"],
        "function": petrotech.bottoms_up_time,
    },
}


@petrotech_api.route("/api/petrotech/calculations", methods=["GET"])
def list_petrotech_calculations():
    return jsonify({
        "status": "success",
        "calculations": {
            name: {
                "label": item["label"],
                "fields": item["fields"],
                "units": item["units"],
            }
            for name, item in PETROTECH_CALCULATIONS.items()
        },
    })


@petrotech_api.route("/api/petrotech/calculate", methods=["POST"])
def calculate_petrotech():
    data = request.get_json(silent=True) or {}
    name = data.get("calculation")

    if name not in PETROTECH_CALCULATIONS:
        return jsonify({"error": "Unknown PetroTech calculation."}), 400

    item = PETROTECH_CALCULATIONS[name]
    inputs = data.get("inputs") or {}

    try:
        values = []

        for field in item["fields"]:
            raw = inputs.get(field)

            if raw is None or str(raw).strip() == "":
                return jsonify({
                    "error": f"Missing required input: {field}"
                }), 400

            values.append(float(raw))

        result = item["function"](*values)

        return jsonify({
            "status": "success",
            "calculation": name,
            "label": item["label"],
            "result": round(result, 6),
            "units": item["units"],
        })

    except (ValueError, TypeError, ZeroDivisionError) as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({"error": "Calculation failed unexpectedly."}), 500
