def hydrostatic_pressure():
    print("\n--- HYDROSTATIC PRESSURE ---")

    mud_weight = float(input("Enter mud weight (ppg): "))
    tvd = float(input("Enter true vertical depth (ft): "))

    pressure = 0.052 * mud_weight * tvd

    print("\n--- RESULTS ---")
    print(f"Mud Weight: {mud_weight:.2f} ppg")
    print(f"TVD: {tvd:.2f} ft")
    print(f"Hydrostatic Pressure: {pressure:.2f} psi")


def formation_pressure():
    print("\n--- FORMATION PRESSURE ---")

    gradient = float(
        input("Enter formation pressure gradient (psi/ft): ")
    )

    tvd = float(
        input("Enter true vertical depth (ft): ")
    )

    pressure = gradient * tvd

    print("\n--- RESULTS ---")
    print(f"Formation Pressure Gradient: {gradient:.4f} psi/ft")
    print(f"TVD: {tvd:.2f} ft")
    print(f"Formation Pressure: {pressure:.2f} psi")