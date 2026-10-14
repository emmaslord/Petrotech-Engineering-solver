
def electrical_power(voltage, current):
    """Electrical power in watts for DC or unity power factor."""
    return voltage * current


def ohms_law(voltage=None, current=None, resistance=None):
    """Calculate one missing quantity from the other two."""
    values = {
        "voltage": voltage,
        "current": current,
        "resistance": resistance,
    }
    supplied = [k for k, v in values.items() if v is not None]

    if len(supplied) != 2:
        raise ValueError("Supply exactly two of voltage, current and resistance.")

    if any(not isinstance(values[k], (int, float)) for k in supplied):
        raise ValueError("Inputs must be numeric.")

    if resistance is not None and resistance < 0:
        raise ValueError("Resistance cannot be negative.")

    if voltage is None:
        return {"voltage": current * resistance}

    if current is None:
        if resistance == 0:
            raise ValueError("Cannot divide by zero resistance.")
        return {"current": voltage / resistance}

    if current == 0:
        raise ValueError("Cannot calculate resistance when current is zero.")

    return {"resistance": voltage / current}
