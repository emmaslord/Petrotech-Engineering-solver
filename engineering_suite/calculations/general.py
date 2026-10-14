def percentage(part, whole):
    """Percentage of a whole."""
    if whole == 0:
        raise ValueError("Whole cannot be zero.")
    return part / whole * 100


def unit_weight(density, gravity=9.81):
    """Weight per unit volume in N/m³."""
    if density < 0 or gravity <= 0:
        raise ValueError("Density must be non-negative and gravity positive.")
    return density * gravity