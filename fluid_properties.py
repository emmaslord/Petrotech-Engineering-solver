def api_gravity():
    print("\n--- API GRAVITY ---")

    sg = float(
        input("Enter oil specific gravity at 60°F: ")
    )

    if sg <= 0:
        print("Specific gravity must be greater than zero.")
        return

    api = (141.5 / sg) - 131.5

    print("\n--- RESULTS ---")
    print(f"Specific Gravity: {sg:.3f}")
    print(f"API Gravity: {api:.2f} °API")


def specific_gravity():
    print("\n--- SPECIFIC GRAVITY ---")

    api = float(
        input("Enter API gravity (°API): ")
    )

    if api <= -131.5:
        print("Invalid API gravity value.")
        return

    sg = 141.5 / (api + 131.5)

    print("\n--- RESULTS ---")
    print(f"API Gravity: {api:.2f} °API")
    print(f"Specific Gravity: {sg:.3f}")