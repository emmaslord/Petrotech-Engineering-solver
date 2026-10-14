def ooip():
    print("\n--- ORIGINAL OIL IN PLACE (OOIP) ---")
    print("Volumetric Method")
    
    area = float(input("Enter reservoir area (acres): "))
    thickness = float(input("Enter net pay thickness (ft): "))
    porosity = float(input("Enter porosity (fraction): "))
    water_saturation = float(
        input("Enter initial water saturation (fraction): ")
    )
    boi = float(
        input("Enter initial oil FVF, Boi (rb/STB): ")
    )

    if area <= 0 or thickness <= 0:
        print("Area and thickness must be greater than zero.")
        return

    if not 0 < porosity < 1:
        print("Porosity must be between 0 and 1.")
        return

    if not 0 <= water_saturation < 1:
        print("Water saturation must be between 0 and 1.")
        return

    if boi <= 0:
        print("Boi must be greater than zero.")
        return

    ooip = (
        7758
        * area
        * thickness
        * porosity
        * (1 - water_saturation)
        / boi
    )

    print("\n--- RESULTS ---")
    print(f"Reservoir Area: {area:.2f} acres")
    print(f"Net Pay: {thickness:.2f} ft")
    print(f"Porosity: {porosity:.3f}")
    print(f"Water Saturation: {water_saturation:.3f}")
    print(f"Boi: {boi:.4f} rb/STB")
    print(f"OOIP: {ooip:,.2f} STB")
    
    
    
def ogip():
    print("\n--- ORIGINAL GAS IN PLACE (OGIP) ---")
    print("Volumetric Method")

    area = float(input("Enter reservoir area (acres): "))
    thickness = float(input("Enter net pay thickness (ft): "))
    porosity = float(input("Enter porosity (fraction): "))
    water_saturation = float(
        input("Enter initial water saturation (fraction): ")
    )
    bgi = float(
        input("Enter initial gas FVF, Bgi (reservoir ft3/scf): ")
    )

    if area <= 0 or thickness <= 0:
        print("Area and thickness must be greater than zero.")
        return

    if not 0 < porosity < 1:
        print("Porosity must be between 0 and 1.")
        return

    if not 0 <= water_saturation < 1:
        print("Water saturation must be between 0 and 1.")
        return

    if bgi <= 0:
        print("Bgi must be greater than zero.")
        return

    ogip = (
        43560
        * area
        * thickness
        * porosity
        * (1 - water_saturation)
        / bgi
    )

    print("\n--- RESULTS ---")
    print(f"OGIP: {ogip:,.2f} scf")
    print(f"OGIP: {ogip / 1_000_000:,.4f} MMscf")
    print(f"OGIP: {ogip / 1_000_000_000:,.6f} Bscf")