
from calculations import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_weight,
    api_gravity,
    specific_gravity,
    ooip,
    ogip,
    annular_velocity,
    pipe_velocity,
    triplex_pump_output,
    equivalent_circulating_density,
    annular_capacity,
    pipe_capacity,
    hole_capacity,
    wellbore_volume,
    annular_volume,
    bottoms_up_time,
)


def get_float(prompt):
    """Read a numeric input and handle invalid entries."""
    try:
        return float(input(prompt))
    except ValueError:
        raise ValueError("Please enter a valid number.")


def run_calculation(title, function, prompts, labels):
    print(f"\n--- {title} ---")

    try:
        values = [get_float(prompt) for prompt in prompts]
        result = function(*values)
        print(f"\nResult: {result:,.4f}")
        if labels:
            print(labels)
    except ValueError as error:
        print(f"\nInput error: {error}")


def main():
    while True:
        print("\n====================================")
        print("       PETROTECH MASTER v1.0")
        print("   Petroleum Engineering Calculator")
        print("====================================")

        print("\n--- PRESSURE ---")
        print("1. Hydrostatic Pressure")
        print("2. Formation Pressure")
        print("3. Required Mud Weight")
        print("4. Equivalent Circulating Density")

        print("\n--- FLUID PROPERTIES ---")
        print("5. API Gravity")
        print("6. Specific Gravity")

        print("\n--- FLOW AND PUMPS ---")
        print("7. Annular Velocity")
        print("8. Pipe Velocity")
        print("9. Triplex Pump Output")

        print("\n--- WELL GEOMETRY AND VOLUME ---")
        print("10. Annular Capacity")
        print("11. Pipe Capacity")
        print("12. Hole Capacity")
        print("13. Wellbore Volume")
        print("14. Annular Volume")
        print("15. Bottoms-Up Circulation Time")

        print("\n--- RESERVOIR ---")
        print("16. Original Oil In Place (OOIP)")
        print("17. Original Gas In Place (OGIP)")

        print("\n0. Exit")

        choice = input("\nChoose an option: ").strip()

        options = {
            "1": (
                "Hydrostatic Pressure",
                hydrostatic_pressure,
                ["Mud weight (ppg): ", "True vertical depth (ft): "],
                "Pressure in psi",
            ),
            "2": (
                "Formation Pressure",
                formation_pressure,
                ["Pressure gradient (psi/ft): ", "TVD (ft): "],
                "Pressure in psi",
            ),
            "3": (
                "Required Mud Weight",
                required_mud_weight,
                ["Target pressure (psi): ", "TVD (ft): "],
                "Mud weight in ppg",
            ),
            "4": (
                "Equivalent Circulating Density",
                equivalent_circulating_density,
                [
                    "Mud weight (ppg): ",
                    "Annular pressure loss (psi): ",
                    "TVD (ft): ",
                ],
                "ECD in ppg",
            ),
            "5": (
                "API Gravity",
                api_gravity,
                ["Specific gravity: "],
                "API degrees",
            ),
            "6": (
                "Specific Gravity",
                specific_gravity,
                ["API gravity: "],
                "Specific gravity",
            ),
            "7": (
                "Annular Velocity",
                annular_velocity,
                [
                    "Flow rate (US gpm): ",
                    "Hole diameter (in): ",
                    "Pipe outside diameter (in): ",
                ],
                "Velocity in ft/min",
            ),
            "8": (
                "Pipe Velocity",
                pipe_velocity,
                ["Flow rate (US gpm): ", "Pipe inside diameter (in): "],
                "Velocity in ft/min",
            ),
            "9": (
                "Triplex Pump Output",
                triplex_pump_output,
                [
                    "Liner diameter (in): ",
                    "Stroke length (in): ",
                    "Strokes per minute: ",
                    "Volumetric efficiency (0-1, e.g. 0.90): ",
                ],
                "Pump output in US gpm",
            ),
            "10": (
                "Annular Capacity",
                annular_capacity,
                ["Hole diameter (in): ", "Pipe outside diameter (in): "],
                "Capacity in bbl/ft",
            ),
            "11": (
                "Pipe Capacity",
                pipe_capacity,
                ["Pipe inside diameter (in): "],
                "Capacity in bbl/ft",
            ),
            "12": (
                "Hole Capacity",
                hole_capacity,
                ["Hole diameter (in): "],
                "Capacity in bbl/ft",
            ),
            "13": (
                "Wellbore Volume",
                wellbore_volume,
                ["Hole diameter (in): ", "Length (ft): "],
                "Volume in barrels",
            ),
            "14": (
                "Annular Volume",
                annular_volume,
                [
                    "Hole diameter (in): ",
                    "Pipe outside diameter (in): ",
                    "Annular length (ft): ",
                ],
                "Volume in barrels",
            ),
            "15": (
                "Bottoms-Up Time",
                bottoms_up_time,
                [
                    "Annular capacity (bbl/ft): ",
                    "Annular length (ft): ",
                    "Flow rate (bbl/min): ",
                ],
                "Time in minutes",
            ),
            "16": (
                "OOIP",
                ooip,
                [
                    "Area (acres): ",
                    "Net pay (ft): ",
                    "Porosity (fraction, e.g. 0.20): ",
                    "Water saturation (fraction, e.g. 0.30): ",
                    "Oil formation volume factor Boi (rb/STB): ",
                ],
                "Estimated stock-tank barrels",
            ),
            "17": (
                "OGIP",
                ogip,
                [
                    "Area (acres): ",
                    "Net pay (ft): ",
                    "Porosity (fraction, e.g. 0.20): ",
                    "Water saturation (fraction, e.g. 0.30): ",
                    "Gas formation volume factor Bgi (res ft3/scf): ",
                ],
                "Estimated standard cubic feet",
            ),
        }

        if choice == "0":
            print("\nThank you for using PetroTech.")
            break

        if choice not in options:
            print("\nInvalid option. Choose a number from 0 to 17.")
            continue

        title, function, prompts, units = options[choice]
        run_calculation(title, function, prompts, units)


if __name__ == "__main__":
    main()
