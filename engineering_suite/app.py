from calculations import petrotech
from petrotech_api import petrotech_api
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.register_blueprint(petrotech_api)

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "success",
        "message": "Engineering Technology Solver API is running",
        "version": "1.0"
    })


from calculations.petroleum import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_density,
    api_gravity,
    specific_gravity_from_api,
    annular_velocity,
    pipe_velocity,
)
from calculations.mechanical import force, pressure, kinetic_energy, density
from calculations.electrical import electrical_power, ohms_law
from calculations.civil import rectangle_area, circle_area
from calculations.general import percentage, unit_weight



CALCULATIONS = {
    "hydrostatic_pressure": {
        "label": "Hydrostatic Pressure",
        "category": "Petroleum Engineering",
        "fields": ["mud_density", "depth"],
        "units": ["kg/m³", "m"],
    },
    "formation_pressure": {
        "label": "Formation Pressure",
        "category": "Petroleum Engineering",
        "fields": ["pressure_gradient", "depth"],
        "units": ["Pa/m", "m"],
    },
    "required_mud_density": {
        "label": "Required Mud Density",
        "category": "Petroleum Engineering",
        "fields": ["formation_pressure", "depth"],
        "units": ["Pa", "m"],
    },
    "api_gravity": {
        "label": "API Gravity",
        "category": "Petroleum Engineering",
        "fields": ["specific_gravity"],
        "units": [""],
    },
    "specific_gravity_from_api": {
        "label": "Specific Gravity from API",
        "category": "Petroleum Engineering",
        "fields": ["api_value"],
        "units": ["°API"],
    },
    "annular_velocity": {
        "label": "Annular Velocity",
        "category": "Petroleum Engineering",
        "fields": ["flow_rate", "hole_diameter", "pipe_outer_diameter"],
        "units": ["m³/s", "m", "m"],
    },
    "pipe_velocity": {
        "label": "Pipe Velocity",
        "category": "Petroleum Engineering",
        "fields": ["flow_rate", "pipe_inner_diameter"],
        "units": ["m³/s", "m"],
    },
    "force": {
        "label": "Force",
        "category": "Mechanical Engineering",
        "fields": ["mass", "acceleration"],
        "units": ["kg", "m/s²"],
    },
    "pressure": {
        "label": "Pressure",
        "category": "Mechanical Engineering",
        "fields": ["force_value", "area"],
        "units": ["N", "m²"],
    },
    "kinetic_energy": {
        "label": "Kinetic Energy",
        "category": "Mechanical Engineering",
        "fields": ["mass", "velocity"],
        "units": ["kg", "m/s"],
    },
    "density": {
        "label": "Density",
        "category": "Mechanical Engineering",
        "fields": ["mass", "volume"],
        "units": ["kg", "m³"],
    },
    "electrical_power": {
        "label": "Electrical Power",
        "category": "Electrical Engineering",
        "fields": ["voltage", "current"],
        "units": ["V", "A"],
    },
    "rectangle_area": {
        "label": "Rectangle Area",
        "category": "Civil Engineering",
        "fields": ["length", "width"],
        "units": ["m", "m"],
    },
    "circle_area": {
        "label": "Circle Area",
        "category": "Civil Engineering",
        "fields": ["radius"],
        "units": ["m"],
    },
    "percentage": {
        "label": "Percentage",
        "category": "General Engineering",
        "fields": ["part", "whole"],
        "units": ["", ""],
    },
    "unit_weight": {
        "label": "Unit Weight",
        "category": "General Engineering",
        "fields": ["density", "gravity"],
        "units": ["kg/m³", "m/s²"],
    },
}


def calculate(name, values):
    if name == "hydrostatic_pressure":
        return hydrostatic_pressure(values["mud_density"], values["depth"])
    if name == "formation_pressure":
        return formation_pressure(values["pressure_gradient"], values["depth"])
    if name == "required_mud_density":
        return required_mud_density(values["formation_pressure"], values["depth"])
    if name == "api_gravity":
        return api_gravity(values["specific_gravity"])
    if name == "specific_gravity_from_api":
        return specific_gravity_from_api(values["api_value"])
    if name == "annular_velocity":
        return annular_velocity(
            values["flow_rate"], values["hole_diameter"],
            values["pipe_outer_diameter"]
        )
    if name == "pipe_velocity":
        return pipe_velocity(values["flow_rate"], values["pipe_inner_diameter"])
    if name == "force":
        return force(values["mass"], values["acceleration"])
    if name == "pressure":
        return pressure(values["force_value"], values["area"])
    if name == "kinetic_energy":
        return kinetic_energy(values["mass"], values["velocity"])
    if name == "density":
        return density(values["mass"], values["volume"])
    if name == "electrical_power":
        return electrical_power(values["voltage"], values["current"])
    if name == "rectangle_area":
        return rectangle_area(values["length"], values["width"])
    if name == "circle_area":
        return circle_area(values["radius"])
    if name == "percentage":
        return percentage(values["part"], values["whole"])
    if name == "unit_weight":
        return unit_weight(values["density"], values["gravity"])
    raise ValueError("Unknown calculation selected.")


@app.route("/")
def index():
    return render_template("index.html", calculations=CALCULATIONS)


@app.route("/calculate", methods=["POST"])
def calculate_route():
    try:
        data = request.get_json(silent=True) or {}
        name = data.get("calculation")

        if name not in CALCULATIONS:
            return jsonify({"error": "Please select a valid calculation."}), 400

        fields = CALCULATIONS[name]["fields"]
        values = {}

        for field in fields:
            raw = data.get("inputs", {}).get(field)
            if raw is None or str(raw).strip() == "":
                return jsonify({"error": f"Enter a value for {field.replace('_', ' ')}."}), 400
            values[field] = float(raw)

        result = calculate(name, values)

        return jsonify({
            "result": round(result, 6),
            "category": CALCULATIONS[name]["category"],
        })

    except (ValueError, TypeError, ZeroDivisionError) as error:
        return jsonify({"error": str(error) or "Please check your input values."}), 400
    except Exception:
        app.logger.exception("Unexpected calculation error")
        return jsonify({"error": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5002)
