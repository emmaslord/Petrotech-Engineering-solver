
from flask import Flask, render_template, request
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

app = Flask(__name__)

# Calculations available in the web interface
CALCULATIONS = {
    "Petroleum": {
        "Hydrostatic Pressure": {
            "function": "hydrostatic_pressure",
            "fields": [
                ("mud_density", "Fluid density (kg/m³)"),
                ("true_vertical_depth", "True vertical depth (m)"),
            ],
            "unit": "Pa",
        },
    },
    "Mechanical": {
        "Force": {
            "function": "force",
            "fields": [
                ("mass", "Mass (kg)"),
                ("acceleration", "Acceleration (m/s²)"),
            ],
            "unit": "N",
        },
        "Pressure": {
            "function": "pressure",
            "fields": [
                ("force_value", "Force (N)"),
                ("area", "Area (m²)"),
            ],
            "unit": "Pa",
        },
        "Kinetic Energy": {
            "function": "kinetic_energy",
            "fields": [
                ("mass", "Mass (kg)"),
                ("velocity", "Velocity (m/s)"),
            ],
            "unit": "J",
        },
    },
    "Electrical": {
        "Electrical Power": {
            "function": "electrical_power",
            "fields": [
                ("voltage", "Voltage (V)"),
                ("current", "Current (A)"),
            ],
            "unit": "W",
        },
    },
    "Civil": {
        "Rectangle Area": {
            "function": "rectangle_area",
            "fields": [
                ("length", "Length (m)"),
                ("width", "Width (m)"),
            ],
            "unit": "m²",
        },
        "Circle Area": {
            "function": "circle_area",
            "fields": [
                ("radius", "Radius (m)"),
            ],
            "unit": "m²",
        },
    },
    "Mathematics": {
        "Density": {
            "function": "density",
            "fields": [
                ("mass", "Mass (kg)"),
                ("volume", "Volume (m³)"),
            ],
            "unit": "kg/m³",
        },
    },
}

FUNCTIONS = {
    "hydrostatic_pressure": hydrostatic_pressure,
    "force": force,
    "pressure": pressure,
    "kinetic_energy": kinetic_energy,
    "electrical_power": electrical_power,
    "rectangle_area": rectangle_area,
    "circle_area": circle_area,
    "density": density,
}


@app.route("/", methods=["GET", "POST"])
def home():
    disciplines = list(CALCULATIONS.keys())

    discipline = request.values.get(
        "discipline", "Petroleum"
    )

    if discipline not in CALCULATIONS:
        discipline = "Petroleum"

    available = CALCULATIONS[discipline]
    calculation_names = list(available.keys())

    calculation = request.values.get(
        "calculation", calculation_names[0]
    )

    if calculation not in available:
        calculation = calculation_names[0]

    config = available[calculation]
    result = None
    error = None

    if request.method == "POST":
        values = {}

        try:
            for field_name, label in config["fields"]:
                raw_value = request.form.get(
                    field_name, ""
                ).strip()

                if not raw_value:
                    raise ValueError(
                        f"Please enter {label.lower()}."
                    )

                value = float(raw_value)

                if not __import__("math").isfinite(value):
                    raise ValueError(
                        f"{label} must be a finite number."
                    )

                values[field_name] = value

            function_name = config["function"]
            function = FUNCTIONS.get(function_name)

            if function is None:
                raise ValueError(
                    "This calculation is not available yet."
                )

            answer = function(**values)

            result = {
                "value": answer,
                "unit": config["unit"],
                "calculation": calculation,
            }

        except (ValueError, TypeError, OverflowError) as exc:
            error = str(exc) or "Please check your input values."

    return render_template(
        "index.html",
        disciplines=disciplines,
        calculations=available,
        discipline=discipline,
        calculation=calculation,
        config=config,
        result=result,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
