def oil_formation_volume_factor():
    print("\n--- OIL FORMATION VOLUME FACTOR (Bo) ---")
    print("Standing Correlation")

    rs = float(input("Enter solution gas-oil ratio (scf/STB): "))
    gas_sg = float(input("Enter gas specific gravity: "))
    oil_sg = float(input("Enter oil specific gravity: "))
    temperature = float(input("Enter reservoir temperature (°F): "))

    if rs < 0 or gas_sg <= 0 or oil_sg <= 0:
        print("Invalid input.")
        return

    bo = (
        0.9759
        + 0.000120
        * (
            rs * (gas_sg / oil_sg) ** 0.5
            + 1.25 * temperature
        ) ** 1.2
    )

    print("\n--- RESULTS ---")
    print(f"Bo: {bo:.4f} rb/STB")


def gas_formation_volume_factor():
    print("\n--- GAS FORMATION VOLUME FACTOR (Bg) ---")

    pressure = float(input("Enter pressure (psia): "))
    temperature_f = float(input("Enter temperature (°F): "))
    z = float(input("Enter gas compressibility factor (Z): "))

    if pressure <= 0 or z <= 0:
        print("Invalid input.")
        return

    temperature_r = temperature_f + 459.67

    bg = (0.02827 * z * temperature_r) / pressure

    print("\n--- RESULTS ---")
    print(f"Temperature: {temperature_r:.2f} °R")
    print(f"Bg: {bg:.6f} ft³/scf") 