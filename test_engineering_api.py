
from engineering_api_client import (
    check_api_health,
    get_petrotech_calculations,
    calculate_petrotech,
)

print("1. Checking API health...")
print(check_api_health())

print("\n2. Loading PetroTech calculations...")
calculations = get_petrotech_calculations()
print("Available calculations:", len(calculations["calculations"]))

print("\n3. Testing hydrostatic pressure...")
result = calculate_petrotech(
    "petrotech_hydrostatic_pressure",
    {
        "mud_weight_ppg": 10,
        "tvd_ft": 5000,
    },
)
print(result)

