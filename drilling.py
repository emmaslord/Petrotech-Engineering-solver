def mud_weight():
    print("\n--- MUD WEIGHT ---")

    pressure = float(
        input("Enter required pressure (psi): ")
    )

    tvd = float(
        input("Enter true vertical depth (ft): ")
    )

    mw = pressure / (0.052 * tvd)

    print("\n--- RESULTS ---")
    print(f"Required Pressure: {pressure:.2f} psi")
    print(f"TVD: {tvd:.2f} ft")
    print(f"Required Mud Weight: {mw:.2f} ppg")