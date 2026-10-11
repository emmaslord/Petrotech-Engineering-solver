
import re

from calculations import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_weight,
    equivalent_circulating_density,
    api_gravity,
    specific_gravity,
    ooip,
    ogip,
    annular_velocity,
    pipe_velocity,
    triplex_pump_output,
    hole_capacity,
    pipe_capacity,
    annular_capacity,
    wellbore_volume,
    annular_volume,
    bottoms_up_time,
)
from ai_fallback import ask_groq


NUMBER = r"(-?\d+(?:\.\d+)?)"


def get_number(text, *labels):
    """Find a number associated with one of the supplied labels."""
    for label in sorted(labels, key=len, reverse=True):
        pattern = (
            r"\b" + re.escape(label) +
            r"\b\s*(?:(?:of|is|=|:)\s*)?" +
            r"(-?\d+(?:\.\d+)?)"
        )
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def result(name, given, formula, working, answer, unit):
    return {
        "success": True,
        "calculation": name,
        "given": given,
        "formula": formula,
        "working": working,
        "answer": round(answer, 4),
        "unit": unit,
        "message": "Calculation completed successfully.",
    }


def missing(name, fields):
    return {
        "success": False,
        "message": (
            f"To calculate {name}, include these values: "
            + ", ".join(fields)
            + "."
        ),
    }


def solve_question(question):
    """Solve supported petroleum engineering questions."""

    text = question.lower().replace(",", "")

    try:
        # 1. Required mud weight
        if "required mud weight" in text or "calculate mud weight" in text:
            pressure = get_number(
                text, "formation pressure", "pressure"
            )
            depth = get_number(
                text, "true vertical depth", "tvd", "depth"
            )

            if pressure is None or depth is None:
                return missing(
                    "required mud weight",
                    ["pressure in psi", "TVD/depth in ft"],
                )

            answer = required_mud_weight(pressure, depth)
            return result(
                "Required Mud Weight",
                {"Pressure": f"{pressure:g} psi",
                 "TVD": f"{depth:g} ft"},
                "Mud weight = pressure / (0.052 × TVD)",
                f"{pressure:g} / (0.052 × {depth:g})",
                answer, "ppg",
            )

        # 2. Equivalent circulating density
        if "equivalent circulating density" in text or re.search(
            r"\b(?:ecd)\b", text
        ):
            mud = get_number(text, "mud weight", "mud wt", "mw")
            loss = get_number(
                text, "annular pressure loss", "pressure loss", "friction loss"
            )
            depth = get_number(
                text, "true vertical depth", "tvd", "depth"
            )

            if None in (mud, loss, depth):
                return missing(
                    "ECD",
                    ["mud weight in ppg",
                     "annular pressure loss in psi", "TVD in ft"],
                )

            answer = equivalent_circulating_density(mud, loss, depth)
            return result(
                "Equivalent Circulating Density",
                {"Mud weight": f"{mud:g} ppg",
                 "Pressure loss": f"{loss:g} psi",
                 "TVD": f"{depth:g} ft"},
                "ECD = mud weight + pressure loss / (0.052 × TVD)",
                f"{mud:g} + {loss:g} / (0.052 × {depth:g})",
                answer, "ppg",
            )

        # 3. Hydrostatic pressure
        if "hydrostatic pressure" in text:
            mud = get_number(text, "mud weight", "mud wt", "mw")
            depth = get_number(
                text, "true vertical depth", "tvd", "depth"
            )

            if mud is None or depth is None:
                return missing(
                    "hydrostatic pressure",
                    ["mud weight in ppg", "TVD/depth in ft"],
                )

            answer = hydrostatic_pressure(mud, depth)
            return result(
                "Hydrostatic Pressure",
                {"Mud weight": f"{mud:g} ppg",
                 "TVD": f"{depth:g} ft"},
                "Pressure = 0.052 × mud weight × TVD",
                f"0.052 × {mud:g} × {depth:g}",
                answer, "psi",
            )

        # 4. Formation pressure from gradient and depth
        if "formation pressure" in text:
            gradient = get_number(
                text, "pressure gradient", "gradient"
            )
            depth = get_number(
                text, "true vertical depth", "tvd", "depth"
            )

            if gradient is None or depth is None:
                return missing(
                    "formation pressure",
                    ["pressure gradient in psi/ft", "depth in ft"],
                )

            answer = formation_pressure(gradient, depth)
            return result(
                "Formation Pressure",
                {"Gradient": f"{gradient:g} psi/ft",
                 "Depth": f"{depth:g} ft"},
                "Formation pressure = gradient × depth",
                f"{gradient:g} × {depth:g}",
                answer, "psi",
            )

        # 5. Annular velocity
        if "annular velocity" in text:
            flow = get_number(text, "flow rate", "flow", "gpm")
            hole = get_number(text, "hole diameter", "hole size")
            pipe = get_number(text, "pipe od", "pipe outside diameter")

            if None in (flow, hole, pipe):
                return missing(
                    "annular velocity",
                    ["flow rate in gpm", "hole diameter in inches",
                     "pipe OD in inches"],
                )

            answer = annular_velocity(flow, hole, pipe)
            return result(
                "Annular Velocity",
                {"Flow rate": f"{flow:g} gpm",
                 "Hole diameter": f"{hole:g} in",
                 "Pipe OD": f"{pipe:g} in"},
                "Velocity = 24.51 × flow / (hole² − pipe OD²)",
                f"24.51 × {flow:g} / ({hole:g}² − {pipe:g}²)",
                answer, "ft/min",
            )

        # 6. Pipe velocity
        if "pipe velocity" in text:
            flow = get_number(text, "flow rate", "flow", "gpm")
            diameter = get_number(
                text, "pipe id", "pipe inside diameter", "internal diameter"
            )

            if None in (flow, diameter):
                return missing(
                    "pipe velocity",
                    ["flow rate in gpm", "pipe ID in inches"],
                )

            answer = pipe_velocity(flow, diameter)
            return result(
                "Pipe Velocity",
                {"Flow rate": f"{flow:g} gpm",
                 "Pipe ID": f"{diameter:g} in"},
                "Velocity = 24.51 × flow / pipe ID²",
                f"24.51 × {flow:g} / {diameter:g}²",
                answer, "ft/min",
            )

        # 7. Triplex pump output
        if "triplex" in text or "pump output" in text:
            liner = get_number(text, "liner diameter", "liner size")
            stroke = get_number(text, "stroke length")
            spm = get_number(text, "strokes per minute", "spm")
            efficiency = get_number(
                text, "volumetric efficiency", "efficiency"
            )

            if None in (liner, stroke, spm):
                return missing(
                    "triplex pump output",
                    ["liner diameter in inches",
                     "stroke length in inches", "strokes per minute"],
                )

            if efficiency is None:
                efficiency = 0.90
            elif efficiency > 1:
                efficiency = efficiency / 100

            answer = triplex_pump_output(
                liner, stroke, spm, efficiency
            )
            return result(
                "Triplex Pump Output",
                {"Liner diameter": f"{liner:g} in",
                 "Stroke length": f"{stroke:g} in",
                 "Strokes per minute": f"{spm:g}",
                 "Volumetric efficiency": f"{efficiency:g}"},
                "Triplex pump displacement × volumetric efficiency",
                "Calculated using the triplex pump formula",
                answer, "US gal/min",
            )

        # 8. API gravity from specific gravity
        if "api gravity" in text and (
            "specific gravity" in text or "convert" in text
        ):
            sg = get_number(text, "specific gravity", "sg")

            if sg is None:
                return missing("API gravity", ["specific gravity"])

            answer = api_gravity(sg)
            return result(
                "API Gravity",
                {"Specific gravity": f"{sg:g}"},
                "API = 141.5 / SG − 131.5",
                f"141.5 / {sg:g} − 131.5",
                answer, "degrees API",
            )

        # 9. Specific gravity from API gravity
        if "specific gravity" in text and "api" in text:
            api = get_number(text, "api gravity", "api")

            if api is None:
                return missing("specific gravity", ["API gravity"])

            answer = specific_gravity(api)
            return result(
                "Specific Gravity",
                {"API gravity": f"{api:g} degrees API"},
                "SG = 141.5 / (API + 131.5)",
                f"141.5 / ({api:g} + 131.5)",
                answer, "dimensionless",
            )

        # 10. Bottoms-up circulation time
        if "bottoms up" in text or "bottoms-up" in text:
            capacity = get_number(
                text, "annular capacity", "capacity"
            )
            length = get_number(
                text, "annular length", "annular length ft",
                "length", "tvd", "depth"
            )
            flow = get_number(
                text, "flow rate bbl/min", "flow rate",
                "flow", "bbl/min"
            )

            if None in (capacity, length, flow):
                return missing(
                    "bottoms-up time",
                    ["annular capacity in bbl/ft",
                     "annular length in ft", "flow rate in bbl/min"],
                )

            answer = bottoms_up_time(capacity, length, flow)
            return result(
                "Bottoms-Up Circulation Time",
                {"Annular capacity": f"{capacity:g} bbl/ft",
                 "Annular length": f"{length:g} ft",
                 "Flow rate": f"{flow:g} bbl/min"},
                "Time = capacity × length / flow rate",
                f"{capacity:g} × {length:g} / {flow:g}",
                answer, "minutes",
            )

        # 11. Annular capacity
        if "annular capacity" in text:
            hole = get_number(text, "hole diameter", "hole size")
            pipe = get_number(text, "pipe od", "pipe outside diameter")

            if hole is None or pipe is None:
                return missing(
                    "annular capacity",
                    ["hole diameter in inches", "pipe OD in inches"],
                )

            answer = annular_capacity(hole, pipe)
            return result(
                "Annular Capacity",
                {"Hole diameter": f"{hole:g} in",
                 "Pipe OD": f"{pipe:g} in"},
                "Capacity = (hole² − pipe OD²) / 1029.4",
                f"({hole:g}² − {pipe:g}²) / 1029.4",
                answer, "bbl/ft",
            )

        # 12. Pipe capacity
        if "pipe capacity" in text:
            diameter = get_number(
                text, "pipe id", "pipe inside diameter", "internal diameter"
            )

            if diameter is None:
                return missing("pipe capacity", ["pipe ID in inches"])

            answer = pipe_capacity(diameter)
            return result(
                "Pipe Capacity",
                {"Pipe ID": f"{diameter:g} in"},
                "Capacity = pipe ID² / 1029.4",
                f"{diameter:g}² / 1029.4",
                answer, "bbl/ft",
            )

        # 13. Hole capacity
        if "hole capacity" in text:
            diameter = get_number(text, "hole diameter", "hole size")

            if diameter is None:
                return missing("hole capacity", ["hole diameter in inches"])

            answer = hole_capacity(diameter)
            return result(
                "Hole Capacity",
                {"Hole diameter": f"{diameter:g} in"},
                "Capacity = hole diameter² / 1029.4",
                f"{diameter:g}² / 1029.4",
                answer, "bbl/ft",
            )

        # 14. Annular volume
        if "annular volume" in text:
            hole = get_number(text, "hole diameter", "hole size")
            pipe = get_number(text, "pipe od", "pipe outside diameter")
            length = get_number(text, "length", "interval length")

            if None in (hole, pipe, length):
                return missing(
                    "annular volume",
                    ["hole diameter in inches", "pipe OD in inches",
                     "length in ft"],
                )

            answer = annular_volume(hole, pipe, length)
            return result(
                "Annular Volume",
                {"Hole diameter": f"{hole:g} in",
                 "Pipe OD": f"{pipe:g} in",
                 "Length": f"{length:g} ft"},
                "Volume = annular capacity × length",
                "Calculated using annular capacity and length",
                answer, "bbl",
            )

        # 15. Wellbore volume
        if "wellbore volume" in text:
            hole = get_number(text, "hole diameter", "hole size")
            length = get_number(text, "length", "interval length")

            if hole is None or length is None:
                return missing(
                    "wellbore volume",
                    ["hole diameter in inches", "length in ft"],
                )

            answer = wellbore_volume(hole, length)
            return result(
                "Wellbore Volume",
                {"Hole diameter": f"{hole:g} in",
                 "Length": f"{length:g} ft"},
                "Volume = hole capacity × length",
                "Calculated using hole capacity and length",
                answer, "bbl",
            )

        # 16. OOIP
        if "ooip" in text or "original oil in place" in text:
            area = get_number(text, "area", "area acres")
            pay = get_number(text, "net pay", "net pay thickness")
            porosity = get_number(text, "porosity")
            sw = get_number(
                text, "water saturation", "water sat", "sw"
            )
            bo = get_number(
                text, "boi", "oil formation volume factor",
                "formation volume factor"
            )

            if None in (area, pay, porosity, sw, bo):
                return missing(
                    "OOIP",
                    ["area in acres", "net pay in ft", "porosity",
                     "water saturation", "Boi"],
                )

            if porosity > 1:
                porosity /= 100
            if sw > 1:
                sw /= 100

            answer = ooip(area, pay, porosity, sw, bo)
            return result(
                "Original Oil in Place",
                {"Area": f"{area:g} acres",
                 "Net pay": f"{pay:g} ft",
                 "Porosity": f"{porosity:g}",
                 "Water saturation": f"{sw:g}",
                 "Boi": f"{bo:g} rb/stb"},
                "OOIP = 7758 × A × h × φ × (1 − Sw) / Boi",
                "Calculated using the volumetric oil-in-place equation",
                answer, "STB",
            )

        # 17. OGIP
        if "ogip" in text or "original gas in place" in text:
            area = get_number(text, "area", "area acres")
            pay = get_number(text, "net pay", "net pay thickness")
            porosity = get_number(text, "porosity")
            sw = get_number(
                text, "water saturation", "water sat", "sw"
            )
            bg = get_number(
                text, "bgi", "gas formation volume factor",
                "formation volume factor"
            )

            if None in (area, pay, porosity, sw, bg):
                return missing(
                    "OGIP",
                    ["area in acres", "net pay in ft", "porosity",
                     "water saturation", "Bgi"],
                )

            if porosity > 1:
                porosity /= 100
            if sw > 1:
                sw /= 100

            answer = ogip(area, pay, porosity, sw, bg)
            return result(
                "Original Gas in Place",
                {"Area": f"{area:g} acres",
                 "Net pay": f"{pay:g} ft",
                 "Porosity": f"{porosity:g}",
                 "Water saturation": f"{sw:g}",
                 "Bgi": f"{bg:g} reservoir ft³/scf"},
                "OGIP = 43560 × A × h × φ × (1 − Sw) / Bgi",
                "Calculated using the volumetric gas-in-place equation",
                answer, "scf",
            )

    except ValueError as exc:
        return {"success": False, "message": str(exc)}
    except (TypeError, ZeroDivisionError) as exc:
        return {
            "success": False,
            "message": f"Could not complete the calculation: {exc}",
        }

    # Groq fallback for unsupported questions
    ai_result = ask_groq(question)

    if ai_result["success"]:
        return {
            "success": True,
            "calculation": "AI-assisted Engineering Explanation",
            "given": {},
            "formula": "Provided by AI; verify before use.",
            "working": ai_result["answer"],
            "answer": 0,
            "unit": "",
            "message": "AI explanation generated. Educational use only.",
        }

    return {
        "success": False,
        "message": (
            "The built-in solver does not support this question, "
            "and the Groq fallback failed. "
            + ai_result["message"]
        ),
    }
