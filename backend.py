

from calculations import (
    hydrostatic_pressure,
    formation_pressure,
    required_mud_weight,
)



from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="PetroTech Engineering API",
    description="Backend API for petroleum engineering calculations",
    version="1.0.0"
)


class HydrostaticPressureInput(BaseModel):
    mud_weight_ppg: float = Field(gt=0, description="Mud weight in ppg")
    tvd_ft: float = Field(gt=0, description="True vertical depth in feet")


class FormationPressureInput(BaseModel):
    gradient_psi_ft: float = Field(
        gt=0, description="Pressure gradient in psi/ft"
    )
    tvd_ft: float = Field(gt=0, description="True vertical depth in feet")


class MudWeightInput(BaseModel):
    pressure_psi: float = Field(ge=0, description="Required pressure in psi")
    tvd_ft: float = Field(gt=0, description="True vertical depth in feet")


@app.get("/")
def home():
    return {
        "application": "PetroTech",
        "status": "online",
        "message": "Petroleum engineering calculation API"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}



@app.post("/calculate/hydrostatic-pressure")
def calculate_hydrostatic_pressure(data: HydrostaticPressureInput):
    try:
        result = hydrostatic_pressure(
            data.mud_weight_ppg,
            data.tvd_ft
        )
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "calculation": "Hydrostatic Pressure",
        "input": data.model_dump(),
        "result": round(result, 2),
        "unit": "psi",
        "formula": "0.052 × mud weight (ppg) × TVD (ft)"
    }



@app.post("/calculate/formation-pressure")
def calculate_formation_pressure(data: FormationPressureInput):
    pressure_psi = data.gradient_psi_ft * data.tvd_ft

    return {
        "calculation": "Formation Pressure",
        "input": data.model_dump(),
        "result": round(pressure_psi, 2),
        "unit": "psi",
        "formula": "pressure gradient (psi/ft) × TVD (ft)"
    }


@app.post("/calculate/mud-weight")
def calculate_mud_weight(data: MudWeightInput):
    mud_weight_ppg = data.pressure_psi / (0.052 * data.tvd_ft)

    return {
        "calculation": "Required Mud Weight",
        "input": data.model_dump(),
        "result": round(mud_weight_ppg, 3),
        "unit": "ppg",
        "formula": "pressure (psi) / (0.052 × TVD (ft))"
    }
