
const calculationData = window.calculationData || {};

const disciplineSelect = document.getElementById("discipline");
const calculationSelect = document.getElementById("calculation");
const inputFields = document.getElementById("input-fields");
const resultElement = document.getElementById("result");
const resultCategory = document.getElementById("result-category");
const resultMessage = document.getElementById("result-message");
const resultStatus = document.getElementById("result-status");
const resetButton = document.getElementById("reset-button");

const fieldLabels = {
    mud_density: "Mud density (kg/m³)",
    depth: "Depth (m)",
    pressure_gradient: "Pressure gradient (Pa/m)",
    formation_pressure: "Formation pressure (Pa)",
    specific_gravity: "Specific gravity",
    api_value: "API gravity (°API)",
    flow_rate: "Flow rate (m³/s)",
    hole_diameter: "Hole diameter (m)",
    pipe_outer_diameter: "Pipe outer diameter (m)",
    pipe_inner_diameter: "Pipe inner diameter (m)",
    mass: "Mass (kg)",
    acceleration: "Acceleration (m/s²)",
    force_value: "Force (N)",
    area: "Area (m²)",
    velocity: "Velocity (m/s)",
    volume: "Volume (m³)",
    voltage: "Voltage (V)",
    current: "Current (A)",
    length: "Length (m)",
    width: "Width (m)",
    radius: "Radius (m)",
    part: "Part",
    whole: "Whole",
    density: "Density (kg/m³)",
    gravity: "Gravity (m/s²)",

    mud_weight_ppg: "Mud weight (ppg)",
    tvd_ft: "True vertical depth (ft)",
    gradient_psi_ft: "Pressure gradient (psi/ft)",
    pressure_psi: "Formation pressure (psi)",
    annular_pressure_loss_psi: "Annular pressure loss (psi)",
    api: "API gravity (°API)",
    area_acres: "Reservoir area (acres)",
    net_pay_ft: "Net pay thickness (ft)",
    porosity: "Porosity (fraction)",
    water_saturation: "Water saturation (fraction)",
    boi_rb_stb: "Initial oil formation volume factor (rb/STB)",
    bgi_res_ft3_scf: "Initial gas formation volume factor (res ft³/scf)",
    flow_rate_gpm: "Flow rate (US GPM)",
    hole_diameter_in: "Hole diameter (in)",
    pipe_od_in: "Pipe outer diameter (in)",
    pipe_id_in: "Pipe inner diameter (in)",
    liner_diameter_in: "Pump liner diameter (in)",
    stroke_length_in: "Stroke length (in)",
    strokes_per_min: "Pump strokes per minute",
    volumetric_efficiency: "Volumetric efficiency (fraction)",
    length_ft: "Length (ft)",
    annular_capacity_bbl_ft: "Annular capacity (bbl/ft)",
    annular_length_ft: "Annular length (ft)",
    flow_rate_bbl_min: "Flow rate (bbl/min)"
};

const resultUnits = {
    petrotech_hydrostatic_pressure: "psi",
    petrotech_formation_pressure: "psi",
    petrotech_required_mud_weight: "ppg",
    petrotech_ecd: "ppg",
    petrotech_api_gravity: "°API",
    petrotech_specific_gravity: "SG",
    petrotech_ooip: "STB",
    petrotech_ogip: "scf",
    petrotech_annular_velocity: "ft/min",
    petrotech_pipe_velocity: "ft/min",
    petrotech_triplex_pump_output: "US GPM",
    petrotech_hole_capacity: "bbl/ft",
    petrotech_pipe_capacity: "bbl/ft",
    petrotech_annular_capacity: "bbl/ft",
    petrotech_wellbore_volume: "bbl",
    petrotech_annular_volume: "bbl",
    petrotech_bottoms_up_time: "min"
};

function formatLabel(field) {
    return fieldLabels[field] || field.replaceAll("_", " ");
}

function ensurePetroTechOption() {
    const exists = [...disciplineSelect.options].some(
        option => option.value === "PetroTech"
    );

    if (!exists) {
        disciplineSelect.add(
            new Option("PetroTech", "PetroTech")
        );
    }
}

function populateCalculations() {
    const selectedDiscipline = disciplineSelect.value;

    const available = Object.entries(calculationData).filter(
        ([, item]) =>
            selectedDiscipline === "All" ||
            item.category === selectedDiscipline
    );

    calculationSelect.innerHTML = "";

    for (const [key, item] of available) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = item.label;
        calculationSelect.appendChild(option);
    }

    renderInputs();

    document.getElementById("calculation-count").textContent =
        Object.keys(calculationData).length;
}

function renderInputs() {
    inputFields.innerHTML = "";

    const selected = calculationData[calculationSelect.value];

    if (!selected) {
        showMessage("No calculation is available.", "Unavailable");
        resultCategory.textContent = "";
        return;
    }

    selected.fields.forEach((field, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "input-field";

        const label = document.createElement("label");
        const input = document.createElement("input");
        const inputId = `input-${field}`;

        const unit = selected.units?.[index];

        label.htmlFor = inputId;
        label.textContent = unit
            ? `${formatLabel(field)}`
            : formatLabel(field);

        input.id = inputId;
        input.name = field;
        input.type = "number";
        input.step = "any";
        input.placeholder = "Enter value";
        input.autocomplete = "off";

        input.addEventListener("input", calculateResult);

        wrapper.append(label, input);
        inputFields.appendChild(wrapper);
    });

    resultElement.textContent = "—";
    resultCategory.textContent = selected.category;
    resultMessage.textContent = "Enter values to calculate.";
    resultStatus.textContent = "Awaiting input";
}

function showMessage(message, status = "Check input") {
    resultElement.textContent = "—";
    resultMessage.textContent = message;
    resultStatus.textContent = status;
}

let requestNumber = 0;

async function calculateResult() {
    const selectedName = calculationSelect.value;
    const selected = calculationData[selectedName];

    if (!selected) return;

    const inputs = {};

    for (const field of selected.fields) {
        const input = inputFields.querySelector(
            `[name="${field}"]`
        );

        if (!input || input.value.trim() === "") {
            requestNumber++;
            showMessage(
                "Enter all required values.",
                "Awaiting input"
            );
            return;
        }

        const number = Number(input.value);

        if (!Number.isFinite(number)) {
            requestNumber++;
            showMessage(
                "Enter valid numeric values.",
                "Invalid input"
            );
            return;
        }

        inputs[field] = number;
    }

    const currentRequest = ++requestNumber;
    const isPetroTech = selectedName.startsWith("petrotech_");

    const endpoint = isPetroTech
        ? "/api/petrotech/calculate"
        : "/calculate";

    resultElement.textContent = "…";
    resultMessage.textContent = "Calculating...";
    resultStatus.textContent = "Processing";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                calculation: selectedName,
                inputs
            })
        });

        const data = await response.json();

        if (currentRequest !== requestNumber) return;

        if (!response.ok) {
            showMessage(
                data.error || "Unable to calculate.",
                "Check input"
            );
            return;
        }

        const formattedResult = Number(data.result).toLocaleString(
            undefined,
            { maximumFractionDigits: 6 }
        );

        const resultUnit = isPetroTech
            ? resultUnits[selectedName]
            : data.unit;

        resultElement.textContent = resultUnit
            ? `${formattedResult} ${resultUnit}`
            : formattedResult;

        resultCategory.textContent =
            data.category || selected.category;

        resultMessage.textContent =
            "Calculation completed. Verify units, assumptions, and input data.";

        resultStatus.textContent = "Calculated";

    } catch (error) {
        if (currentRequest !== requestNumber) return;

        showMessage(
            "Could not reach the calculation server. Check that Flask is running.",
            "Connection error"
        );
    }
}

disciplineSelect.addEventListener(
    "change",
    populateCalculations
);

calculationSelect.addEventListener(
    "change",
    () => {
        requestNumber++;
        renderInputs();
    }
);

resetButton.addEventListener("click", () => {
    inputFields.querySelectorAll("input").forEach(input => {
        input.value = "";
    });

    requestNumber++;

    showMessage(
        "Inputs cleared. Enter new values to calculate.",
        "Reset"
    );
});

async function loadPetroTechCalculations() {
    try {
        const response = await fetch(
            "/api/petrotech/calculations"
        );

        if (!response.ok) {
            throw new Error("PetroTech API unavailable");
        }

        const data = await response.json();

        for (const [key, item] of Object.entries(
            data.calculations || {}
        )) {
            calculationData[key] = {
                label: item.label,
                fields: item.fields,
                units: item.units,
                category: "PetroTech"
            };
        }

        ensurePetroTechOption();
        populateCalculations();

    } catch (error) {
        console.error(
            "Could not load PetroTech calculations:",
            error
        );

        // Keep the existing engineering calculators available.
        populateCalculations();
    }
}

populateCalculations();
loadPetroTechCalculations();
