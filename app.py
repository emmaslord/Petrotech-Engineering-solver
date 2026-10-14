import streamlit as st
import requests

try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    PdfReader = None

from io import BytesIO

import easyocr

import numpy as np

from problem_solver import solve_question

from calculations import (

    hydrostatic_pressure,

    formation_pressure,

    required_mud_weight,

    api_gravity,

    specific_gravity,

    ooip,

    ogip,

    annular_velocity,

    pipe_velocity,

    triplex_pump_output,

    equivalent_circulating_density,

    annular_capacity,

    pipe_capacity,

    hole_capacity,

    wellbore_volume,

    annular_volume,

    bottoms_up_time,

)





# --------------------------------------------------

# ENGINEERING AI

# ---------------------------------------------------



st.set_page_config(
    page_title="Engineering AI",
    page_icon="🛢️",

    layout="wide",

    initial_sidebar_state="expanded",

)



st.markdown("""

<style>

.block-container {

    padding-top: 1.6rem;

    padding-bottom: 2.5rem;

    max-width: 1500px;

}

[data-testid="stSidebar"] {

    background: linear-gradient(180deg, #0b1f35, #102c49);

}

[data-testid="stSidebar"] * {

    color: #f2f7ff;

}

.pt-hero {

    padding: 1.5rem;

    border-radius: 18px;

    background: linear-gradient(120deg, #102c49, #1768a5);

    color: white;

    margin-bottom: 1rem;

}

.pt-hero h1 {

    color: white;

}

.pt-hero p {

    color: #e1efff;

}

div[data-testid="stMetric"] {

    background: rgba(35,131,209,.06);

    border: 1px solid rgba(100,150,200,.22);

    padding: 1rem;

    border-radius: 12px;

}

</style>

""", unsafe_allow_html=True)



# SIDEBAR NAVIGATION



with st.sidebar:

    st.markdown("# 🛢️ Engineering AI")

    st.caption("ENGINEERING SOLVER")

    st.divider()



    page = st.sidebar.radio(

        "Navigation",

        [

            "Dashboard",

            "Calculators",

            "AI Engineering Assistant",

            "Formulas & Reference",
            "Examples & Help",

        ],

    )

    st.divider()

    st.caption("Built for ALL engineering calculations and learning.")

    st.caption("Educational use • v2.0")



st.markdown("""

<div class="pt-hero">

<h1>Engineering AI</h1>

<p>

Engineering calculations, learning resources,

and AI-assisted explanations.

</p>

</div>

""", unsafe_allow_html=True)



# --------------------------------------------------

# DASHBOARD

# --------------------------------------------------



if page == "Dashboard":



    st.subheader("Welcome to your engineering workspace")



    st.write(

        "Calculate common engineering parameters, "

        "study formulas, and explore AI-assisted explanations."

    )



    col1, col2, col3, col4 = st.columns(4)



    col1.metric("Calculation Tools", "17")

    col2.metric("AI Assistant", "Available")

    col3.metric("Input Methods", "Text / PDF / Camera")

    col4.metric("Application Mode", "Educational")



    st.markdown("### Explore your workspace")



    col1, col2 = st.columns(2)



    with col1:

        with st.container(border=True):

            st.subheader("🧮 Calculators")

            st.write(

                "Pressure, mud weight, ECD, fluid velocity, "

                "pump output, capacities, volumes, API gravity, "

                "OOIP and OGIP."

            )



    with col2:

        with st.container(border=True):

            st.subheader("🤖 AI Engineering Assistant")

            st.write(

                "Ask engineering questions, upload question "

                "files, or extract text from a camera image."

            )



    col1, col2 = st.columns(2)



    with col1:

        with st.container(border=True):

            st.subheader("📘 Formulas & Reference")

            st.write(

                "Review formulas, variables, units, and "

                "engineering calculation principles."

            )



    with col2:

        with st.container(border=True):

            st.subheader("🧭 Examples & Help")

            st.write(

                "Try sample questions and learn how to use "

                "the application."

            )



    st.info(

        "Choose a section from the sidebar to begin. "

        "Results are for learning and preliminary checks only."

    )



# --------------------------------------------------

# CALCULATORS

# --------------------------------------------------



elif page == "Calculators":



    st.subheader("Engineering Calculators")



    st.write(

        "Select a calculation, enter the known values, "

        "and review the result and formula."

    )



    calculation = st.selectbox(

        "Choose a calculation",

        [

            "Hydrostatic Pressure",

            "Formation Pressure",

            "Required Mud Weight",

            "Equivalent Circulating Density",

            "API Gravity",

            "Specific Gravity",

            "Annular Velocity",

            "Pipe Velocity",

            "Triplex Pump Output",

            "Annular Capacity",

            "Pipe Capacity",

            "Hole Capacity",

            "Wellbore Volume",

            "Annular Volume",

            "Bottoms-Up Circulation Time",

            "OOIP",

            "OGIP",

        ],

    )



    st.divider()



    if calculation == "Hydrostatic Pressure":



        st.header("Hydrostatic Pressure")



        col1, col2 = st.columns(2)



        with col1:

            mud_weight = st.number_input(

                "Mud Weight (ppg)",

                min_value=0.0,

                value=10.0,

                step=0.1,

            )



        with col2:

            tvd = st.number_input(

                "True Vertical Depth (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

            )



        if mud_weight > 0 and tvd > 0:

            result = hydrostatic_pressure(mud_weight, tvd)

            st.metric("Hydrostatic Pressure", f"{result:,.2f} psi")

            st.caption("Formula: P = 0.052 × Mud Weight × TVD")

        else:

            st.warning("Enter a positive mud weight and depth.")



    elif calculation == "Formation Pressure":



        st.header("Formation Pressure")



        col1, col2 = st.columns(2)



        with col1:

            gradient = st.number_input(

                "Pressure Gradient (psi/ft)",

                min_value=0.0,

                value=0.465,

                step=0.005,

                format="%.3f",

            )



        with col2:

            tvd = st.number_input(

                "True Vertical Depth (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

            )



        result = formation_pressure(gradient, tvd)

        st.metric("Formation Pressure", f"{result:,.2f} psi")

        st.caption("Formula: Pressure = Gradient × TVD")



    elif calculation == "Required Mud Weight":



        st.header("Required Mud Weight")



        col1, col2 = st.columns(2)



        with col1:

            pressure = st.number_input(

                "Target Pressure (psi)",

                min_value=0.0,

                value=2600.0,

                step=50.0,

            )



        with col2:

            tvd = st.number_input(

                "True Vertical Depth (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

            )



        if tvd > 0:

            result = required_mud_weight(pressure, tvd)

            st.metric("Required Mud Weight", f"{result:.2f} ppg")

            st.caption("Formula: MW = Pressure / (0.052 × TVD)")

        else:

            st.warning("TVD must be greater than zero.")



    elif calculation == "Equivalent Circulating Density":



        st.header("Equivalent Circulating Density (ECD)")



        col1, col2 = st.columns(2)



        with col1:

            mud_weight = st.number_input(

                "Mud Weight (ppg)",

                min_value=0.0,

                value=10.0,

                step=0.1,

                key="ecd_mud_weight",

            )



        with col2:

            pressure_loss = st.number_input(

                "Annular Pressure Loss (psi)",

                min_value=0.0,

                value=100.0,

                step=10.0,

                key="ecd_pressure_loss",

            )



        tvd = st.number_input(

            "True Vertical Depth (ft)",

            min_value=0.0,

            value=5000.0,

            step=100.0,

            key="ecd_tvd",

        )



        if tvd > 0:

            result = equivalent_circulating_density(

                mud_weight, pressure_loss, tvd

            )

            st.metric("Equivalent Circulating Density", f"{result:.2f} ppg")

            st.caption(

                "ECD = Mud Weight + Pressure Loss / (0.052 × TVD)"

            )

        else:

            st.warning("TVD must be greater than zero.")





# --------------------------------------------------

# REMAINING CALCULATORS

# --------------------------------------------------



    elif calculation == "Annular Velocity":



        st.header("Annular Velocity")



        col1, col2 = st.columns(2)



        with col1:

            flow_rate = st.number_input(

                "Flow Rate (US gpm)",

                min_value=0.0,

                value=500.0,

                step=10.0,

                key="annular_flow",

            )



            hole_diameter = st.number_input(

                "Hole Diameter (in)",

                min_value=0.1,

                value=8.5,

                step=0.25,

                key="annular_hole",

            )



        with col2:

            pipe_od = st.number_input(

                "Pipe Outside Diameter (in)",

                min_value=0.1,

                value=5.0,

                step=0.25,

                key="annular_pipe",

            )



        if hole_diameter > pipe_od:

            result = annular_velocity(

                flow_rate, hole_diameter, pipe_od

            )

            st.metric("Annular Velocity", f"{result:.2f} ft/min")

        else:

            st.warning(

                "Hole diameter must be greater than pipe outside diameter."

            )



    elif calculation == "Pipe Velocity":



        st.header("Pipe Velocity")



        col1, col2 = st.columns(2)



        with col1:

            flow_rate = st.number_input(

                "Flow Rate (US gpm)",

                min_value=0.0,

                value=500.0,

                step=10.0,

                key="pipe_flow",

            )



        with col2:

            pipe_id = st.number_input(

                "Pipe Inside Diameter (in)",

                min_value=0.1,

                value=4.0,

                step=0.25,

                key="pipe_id",

            )



        result = pipe_velocity(flow_rate, pipe_id)

        st.metric("Pipe Velocity", f"{result:.2f} ft/min")



    elif calculation == "Triplex Pump Output":



        st.header("Triplex Pump Output")



        col1, col2 = st.columns(2)



        with col1:

            liner_diameter = st.number_input(

                "Liner Diameter (in)",

                min_value=0.1,

                value=6.0,

                step=0.25,

            )



            stroke_length = st.number_input(

                "Stroke Length (in)",

                min_value=0.1,

                value=12.0,

                step=1.0,

            )



        with col2:

            strokes_per_min = st.number_input(

                "Strokes per Minute",

                min_value=0.0,

                value=60.0,

                step=5.0,

            )



            efficiency_percent = st.number_input(

                "Volumetric Efficiency (%)",

                min_value=1.0,

                max_value=100.0,

                value=90.0,

                step=5.0,

            )



        result = triplex_pump_output(

            liner_diameter,

            stroke_length,

            strokes_per_min,

            efficiency_percent / 100.0,

        )

        st.metric("Pump Output", f"{result:.2f} US gpm")



    elif calculation == "Annular Capacity":



        st.header("Annular Capacity")



        col1, col2 = st.columns(2)



        with col1:

            hole_diameter = st.number_input(

                "Hole Diameter (in)",

                min_value=0.1,

                value=8.5,

                step=0.25,

                key="ann_cap_hole",

            )



        with col2:

            pipe_od = st.number_input(

                "Pipe Outside Diameter (in)",

                min_value=0.1,

                value=5.0,

                step=0.25,

                key="ann_cap_pipe",

            )



        if hole_diameter > pipe_od:

            result = annular_capacity(hole_diameter, pipe_od)

            st.metric("Annular Capacity", f"{result:.5f} bbl/ft")

        else:

            st.warning("Hole diameter must exceed pipe diameter.")



    elif calculation == "Pipe Capacity":



        st.header("Pipe Capacity")



        pipe_id = st.number_input(

            "Pipe Inside Diameter (in)",

            min_value=0.1,

            value=4.0,

            step=0.25,

        )



        result = pipe_capacity(pipe_id)

        st.metric("Pipe Capacity", f"{result:.5f} bbl/ft")



    elif calculation == "Hole Capacity":



        st.header("Hole Capacity")



        hole_diameter = st.number_input(

            "Hole Diameter (in)",

            min_value=0.1,

            value=8.5,

            step=0.25,

        )



        result = hole_capacity(hole_diameter)

        st.metric("Hole Capacity", f"{result:.5f} bbl/ft")



    elif calculation == "Wellbore Volume":



        st.header("Wellbore Volume")



        col1, col2 = st.columns(2)



        with col1:

            hole_diameter = st.number_input(

                "Hole Diameter (in)",

                min_value=0.1,

                value=8.5,

                step=0.25,

            )



        with col2:

            length = st.number_input(

                "Wellbore Length (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

            )



        result = wellbore_volume(hole_diameter, length)

        st.metric("Wellbore Volume", f"{result:,.3f} bbl")



    elif calculation == "Annular Volume":



        st.header("Annular Volume")



        col1, col2 = st.columns(2)



        with col1:

            hole_diameter = st.number_input(

                "Hole Diameter (in)",

                min_value=0.1,

                value=8.5,

                step=0.25,

                key="ann_vol_hole",

            )



            pipe_od = st.number_input(

                "Pipe Outside Diameter (in)",

                min_value=0.1,

                value=5.0,

                step=0.25,

                key="ann_vol_pipe",

            )



        with col2:

            length = st.number_input(

                "Annular Length (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

                key="ann_vol_length",

            )



        if hole_diameter > pipe_od:

            result = annular_volume(

                hole_diameter, pipe_od, length

            )

            st.metric("Annular Volume", f"{result:,.3f} bbl")

        else:

            st.warning("Hole diameter must exceed pipe diameter.")



    elif calculation == "Bottoms-Up Circulation Time":



        st.header("Bottoms-Up Circulation Time")



        col1, col2 = st.columns(2)



        with col1:

            ann_cap = st.number_input(

                "Annular Capacity (bbl/ft)",

                min_value=0.0001,

                value=0.0435,

                format="%.5f",

            )



            ann_length = st.number_input(

                "Annular Length (ft)",

                min_value=0.0,

                value=5000.0,

                step=100.0,

            )



        with col2:

            flow_rate = st.number_input(

                "Flow Rate (bbl/min)",

                min_value=0.0001,

                value=8.0,

                step=0.5,

            )



        result = bottoms_up_time(

            ann_cap, ann_length, flow_rate

        )

        st.metric("Bottoms-Up Time", f"{result:.2f} minutes")



    elif calculation == "API Gravity":



        st.header("API Gravity")



        sg = st.number_input(

            "Specific Gravity",

            min_value=0.0001,

            value=0.85,

            step=0.01,

            format="%.4f",

        )



        result = api_gravity(sg)

        st.metric("API Gravity", f"{result:.2f}° API")



    elif calculation == "Specific Gravity":



        st.header("Specific Gravity")



        api = st.number_input(

            "API Gravity (° API)",

            min_value=-131.4,

            value=35.0,

            step=1.0,

        )



        result = specific_gravity(api)

        st.metric("Specific Gravity", f"{result:.4f}")



    elif calculation == "OOIP":



        st.header("Original Oil Initially In Place")



        col1, col2 = st.columns(2)



        with col1:

            area = st.number_input(

                "Reservoir Area (acres)",

                min_value=0.0,

                value=640.0,

                step=10.0,

            )



            net_pay = st.number_input(

                "Net Pay (ft)",

                min_value=0.0,

                value=50.0,

                step=5.0,

            )



            porosity = st.number_input(

                "Porosity (fraction)",

                min_value=0.0,

                max_value=1.0,

                value=0.20,

                step=0.01,

            )



        with col2:

            sw = st.number_input(

                "Water Saturation (fraction)",

                min_value=0.0,

                max_value=1.0,

                value=0.30,

                step=0.01,

            )



            boi = st.number_input(

                "Oil Formation Volume Factor (rb/stb)",

                min_value=0.0001,

                value=1.20,

                step=0.05,

            )



        if area > 0 and net_pay > 0:

            result = ooip(area, net_pay, porosity, sw, boi)

            st.metric("OOIP", f"{result:,.2f} STB")

        else:

            st.warning("Enter positive area and net pay.")



    elif calculation == "OGIP":



        st.header("Original Gas Initially In Place")



        col1, col2 = st.columns(2)



        with col1:

            area = st.number_input(

                "Reservoir Area (acres)",

                min_value=0.0,

                value=640.0,

                step=10.0,

                key="ogip_area",

            )



            net_pay = st.number_input(

                "Net Pay (ft)",

                min_value=0.0,

                value=50.0,

                step=5.0,

                key="ogip_net_pay",

            )



            porosity = st.number_input(

                "Porosity (fraction)",

                min_value=0.0,

                max_value=1.0,

                value=0.20,

                step=0.01,

                key="ogip_porosity",

            )



        with col2:

            sw = st.number_input(

                "Water Saturation (fraction)",

                min_value=0.0,

                max_value=1.0,

                value=0.30,

                step=0.01,

                key="ogip_sw",

            )



            bgi = st.number_input(

                "Gas Formation Volume Factor (reservoir ft³/scf)",

                min_value=0.000001,

                value=0.005,

                step=0.001,

                format="%.6f",

                key="ogip_bgi",

            )



        if area > 0 and net_pay > 0:

            result = ogip(area, net_pay, porosity, sw, bgi)

            st.metric("OGIP", f"{result:,.2f} scf")

        else:

            st.warning("Enter positive area and net pay.")





# --------------------------------------------------

# AI ENGINEERING ASSISTANT

# --------------------------------------------------



elif page == "AI Engineering Assistant":



    st.subheader("🤖 AI Engineering Assistant")



    st.write(

        "Ask a petroleum engineering question, upload a TXT or PDF "

        "document, or take a picture of a question."

    )



    st.info(

        "AI-generated explanations may contain errors. "

        "Check formulas, units, assumptions, and results."

    )



    tab1, tab2, tab3 = st.tabs(

        ["💬 Ask a Question", "📄 Upload a File", "📷 Camera OCR"]

    )



    # TEXT QUESTION

    with tab1:



        question = st.text_area(

            "Your engineering question",

            placeholder=(

                "Example: Calculate hydrostatic pressure for "

                "mud weight 12 ppg at TVD 8000 ft."

            ),

            height=140,

            key="assistant_question",

        )



        if st.button("Solve Question", key="assistant_solve"):



            if not question.strip():

                st.warning("Please enter a question.")



            else:

                with st.spinner("Working on your question..."):



                    try:

                        result = solve_question(question.strip())



                        if result.get("success"):



                            st.success(result.get("message", "Solution ready."))



                            st.markdown("### Solution")

                            st.write("**Calculation:**", result.get("calculation", ""))

                            st.write("**Formula:**", result.get("formula", ""))

                            st.write("**Working:**", result.get("working", ""))



                            if result.get("calculation") == (

                                "AI-assisted Engineering Explanation"

                            ):

                                st.info(

                                    "This is an AI-generated explanation. "

                                    "Independently verify technical details."

                                )



                            else:

                                if result.get("given"):

                                    st.write("**Given values:**")



                                    for name, value in result["given"].items():

                                        st.write(f"- {name}: {value}")



                                if result.get("answer") is not None:

                                    st.metric(

                                        "Final Answer",

                                        f'{result["answer"]:,.4f} '

                                        f'{result.get("unit", "")}',

                                    )



                        else:

                            st.warning(

                                result.get(

                                    "message",

                                    "The solver could not answer this question.",

                                )

                            )



                    except Exception as exc:

                        st.error(f"Could not solve the question: {exc}")



    # FILE UPLOAD

    with tab2:



        uploaded_file = st.file_uploader(

            "Upload an engineering question",

            type=["txt", "pdf"],

            key="assistant_file",

        )



        if uploaded_file is not None:



            question_from_file = ""



            try:

                if uploaded_file.name.lower().endswith(".pdf"):



                    pdf = PdfReader(

                        BytesIO(uploaded_file.getvalue())

                    )



                    question_from_file = "\n".join(

                        page.extract_text() or ""

                        for page in pdf.pages

                    ).strip()



                else:

                    question_from_file = uploaded_file.getvalue().decode(

                        "utf-8-sig",

                        errors="replace",

                    ).strip()



                st.text_area(

                    "Extracted text",

                    value=question_from_file,

                    height=180,

                    disabled=True,

                    key="assistant_extracted_text",

                )



                if st.button(

                    "Solve Uploaded Question",

                    key="assistant_file_solve",

                ):



                    if not question_from_file:

                        st.warning(

                            "No text was extracted. The PDF may contain "

                            "scanned pages; try the camera OCR tab."

                        )



                    else:

                        with st.spinner("Solving uploaded question..."):



                            result = solve_question(question_from_file)



                        if result.get("success"):



                            st.success(

                                result.get("message", "Solution ready.")

                            )



                            st.write(

                                "**Calculation:**",

                                result.get("calculation", ""),

                            )



                            st.write(

                                "**Working:**",

                                result.get("working", ""),

                            )



                            if result.get("calculation") == (

                                "AI-assisted Engineering Explanation"

                            ):

                                st.info(

                                    "AI-generated explanation. "

                                    "Verify the formulas and assumptions."

                                )



                            else:

                                st.write(

                                    "**Formula:**",

                                    result.get("formula", ""),

                                )



                                if result.get("given"):

                                    st.write("**Given values:**")



                                    for name, value in result["given"].items():

                                        st.write(f"- {name}: {value}")



                                if result.get("answer") is not None:

                                    st.metric(

                                        "Final Answer",

                                        f'{result["answer"]:,.4f} '

                                        f'{result.get("unit", "")}',

                                    )



                        else:

                            st.warning(

                                result.get(

                                    "message",

                                    "Could not solve the uploaded question.",

                                )

                            )



            except Exception as exc:

                st.error(f"Could not read the uploaded file: {exc}")



    # CAMERA OCR

    with tab3:



        st.write(

            "Capture a clear picture of an engineering question. "

            "Review the extracted text before solving it."

        )



        camera_image = st.camera_input(

            "Take a picture",

            key="assistant_camera",

        )



        if camera_image is not None:



            if st.button(

                "Extract Text",

                key="assistant_extract_camera",

            ):



                with st.spinner("Reading image text..."):



                    try:

                        reader = easyocr.Reader(["en"], gpu=False)



                        image_bytes = camera_image.getvalue()



                        image_array = np.frombuffer(

                            image_bytes,

                            dtype=np.uint8,

                        )



                        extracted_lines = reader.readtext(

                            image_array,

                            detail=0,

                        )



                        extracted_question = "\n".join(

                            extracted_lines

                        ).strip()



                        st.session_state["camera_question_text"] = (

                            extracted_question

                        )



                    except Exception as exc:

                        st.error(f"Could not read the image: {exc}")



            extracted_question = st.session_state.get(

                "camera_question_text",

                "",

            )



            if extracted_question:



                st.text_area(

                    "Review extracted question",

                    value=extracted_question,

                    height=160,

                    key="assistant_camera_review",

                )



                if st.button(

                    "Solve Extracted Question",

                    key="assistant_camera_solve",

                ):



                    with st.spinner("Solving extracted question..."):



                        result = solve_question(extracted_question)



                    if result.get("success"):



                        st.success(

                            result.get("message", "Solution ready.")

                        )



                        st.write(

                            "**Calculation:**",

                            result.get("calculation", ""),

                        )



                        st.write(

                            "**Working:**",

                            result.get("working", ""),

                        )



                        if result.get("calculation") == (

                            "AI-assisted Engineering Explanation"

                        ):

                            st.info(

                                "AI-generated explanation. "

                                "Verify technical details."

                            )



                        else:

                            st.write(

                                "**Formula:**",

                                result.get("formula", ""),

                            )



                            if result.get("given"):

                                st.write("**Given values:**")



                                for name, value in result["given"].items():

                                    st.write(f"- {name}: {value}")



                            if result.get("answer") is not None:

                                st.metric(

                                    "Final Answer",

                                    f'{result["answer"]:,.4f} '

                                    f'{result.get("unit", "")}',

                                )



                    else:

                        st.warning(

                            result.get(

                                "message",

                                "Could not solve the extracted question.",

                            )

                        )



            elif st.session_state.get("camera_question_text") == "":

                st.warning(

                    "No readable text was found. Try a clearer image."

                )



# --------------------------------------------------

# FORMULAS AND REFERENCE

# --------------------------------------------------



elif page == "Formulas & Reference":



    st.subheader("📘 Formulas & Engineering Reference")



    st.write(

        "Use these formulas for learning and preliminary "

        "engineering calculations."

    )



    with st.expander("1. Hydrostatic Pressure", expanded=True):

        st.latex(r"P = 0.052 \times MW \times TVD")

        st.write("MW: mud weight in ppg")

        st.write("TVD: true vertical depth in ft")

        st.write("P: hydrostatic pressure in psi")



    with st.expander("2. Formation Pressure"):

        st.latex(r"P_f = G_f \times TVD")

        st.write("Gf: pressure gradient in psi/ft")



    with st.expander("3. Required Mud Weight"):

        st.latex(r"MW = \frac{P}{0.052 \times TVD}")

        st.write("P: target pressure in psi")



    with st.expander("4. Equivalent Circulating Density"):

        st.latex(

            r"ECD = MW + "

            r"\frac{\Delta P_{\mathrm{annular}}}{0.052 \times TVD}"

        )

        st.write("Annular pressure loss is entered in psi.")



    with st.expander("5. API Gravity"):

        st.latex(r"API = \frac{141.5}{SG} - 131.5")



    with st.expander("6. Specific Gravity"):

        st.latex(r"SG = \frac{141.5}{API + 131.5}")



    with st.expander("7. Annular Velocity"):

        st.write(

            "The app uses flow rate, hole diameter, "

            "and pipe outside diameter."

        )

        st.latex(

            r"V_a = \frac{24.51Q}{D_h^2-D_p^2}"

        )

        st.write(

            "Q: US gpm; diameters: inches. Verify unit conventions "

            "before using the equation in other contexts."

        )



    with st.expander("8. Pipe Velocity"):

        st.latex(r"V_p = \frac{24.51Q}{D_i^2}")

        st.write("Di: pipe inside diameter in inches.")



    with st.expander("9. Annular Capacity"):

        st.latex(

            r"C_a = \frac{D_h^2-D_p^2}{1029.4}"

        )

        st.write("Capacity is expressed in barrels per foot.")



    with st.expander("10. Wellbore Volume"):

        st.latex(r"V = C \times L")

        st.write("C: capacity in bbl/ft; L: length in ft.")



    with st.expander("11. Bottoms-Up Circulation Time"):

        st.latex(

            r"t = \frac{C_a \times L_a}{Q}"

        )

        st.write(

            "Use consistent capacity, length, and flow-rate units."

        )



    with st.expander("12. Original Oil Initially In Place"):

        st.latex(

            r"OOIP = \frac{7758 A h \phi (1-S_w)}{B_{oi}}"

        )

        st.write(

            "A: acres; h: net pay in ft; porosity and water saturation "

            "are fractions; Boi: rb/stb."

        )



    with st.expander("13. Original Gas Initially In Place"):

        st.latex(

            r"OGIP = \frac{43560 A h \phi (1-S_w)}{B_{gi}}"

        )

        st.write(

            "Check the unit convention for Bgi against the formula "

            "used in calculations.py."

        )



# --------------------------------------------------

# EXAMPLES AND HELP

# --------------------------------------------------



elif page == "Examples & Help":



    st.subheader("🧭 Examples & Help")



    st.markdown("### Example questions")



    examples = [

        "Calculate hydrostatic pressure for mud weight 12 ppg at TVD 8000 ft.",

        "Calculate formation pressure for gradient 0.465 psi/ft at TVD 5000 ft.",

        "Calculate required mud weight for pressure 2600 psi at TVD 5000 ft.",

        "Convert specific gravity 0.85 to API gravity.",

        "Calculate annular velocity for flow rate 500 gpm, hole diameter 8.5 in, and pipe OD 5 in.",

        "Explain the difference between hydrostatic pressure and formation pressure.",

    ]



    for index, example in enumerate(examples, start=1):

        st.markdown(f"**{index}.** {example}")



        if st.button(

            "Copy example into assistant",

            key=f"example_{index}",

        ):

            st.session_state["assistant_question"] = example

            st.info(

                "Example saved for the assistant. "

                "Open AI Engineering Assistant and submit it."

            )



    st.divider()



    st.markdown("### How to use PetroTech")



    st.markdown("""

    1. Select a section from the sidebar.

    2. Open Calculators for supported numeric calculations.

    3. Enter values with the requested units.

    4. Review the formula and output.

    5. Use the AI Engineering Assistant for natural-language questions.

    6. Review extracted text carefully when using a PDF or camera.

    """)



    st.warning(

        "This application is intended for educational and preliminary "

        "checks. It is not a substitute for validated engineering "

        "software, professional review, or approved operational procedures."

    )



with st.expander("Engineering AI API Connection"):
    st.write("Test the connection to the Flask calculation API.")

    if st.button("Test Flask API"):
        try:
            response = requests.get(
                "http://127.0.0.1:5001/health",
                timeout=5
            )
            response.raise_for_status()
            result = response.json()

            if result.get("status") == "healthy":
                st.success("Flask API connected successfully!")
            else:
                st.warning(f"Unexpected API response: {result}")

        except requests.RequestException as exc:
            st.error(f"Could not connect to Flask: {exc}")




with st.expander("Flask-Powered Engineering Calculations"):
    calculation_type = st.selectbox(
        "Select calculation",
        [
            "Hydrostatic Pressure",
            "API Gravity"
        ],
        key="flask_calculation_type"
    )

    if calculation_type == "Hydrostatic Pressure":
        mud_weight = st.number_input(
            "Mud weight (ppg)",
            min_value=0.0,
            value=10.0,
            step=0.1,
            key="flask_mud_weight"
        )

        tvd = st.number_input(
            "True vertical depth (ft)",
            min_value=0.0,
            value=5000.0,
            step=100.0,
            key="flask_tvd"
        )

        if st.button("Calculate Hydrostatic Pressure"):
            try:
                response = requests.post(
                    "http://127.0.0.1:5001/api/calculations/hydrostatic-pressure",
                    json={
                        "mud_weight_ppg": mud_weight,
                        "tvd_ft": tvd
                    },
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()

                st.metric(
                    "Hydrostatic Pressure",
                    f"{result['pressure_psi']:,.2f} psi"
                )

            except requests.RequestException as exc:
                st.error(f"Flask API request failed: {exc}")

    else:
        specific_gravity = st.number_input(
            "Oil specific gravity",
            min_value=0.001,
            value=0.85,
            step=0.01,
            key="flask_specific_gravity"
        )

        if st.button("Calculate API Gravity"):
            try:
                response = requests.post(
                    "http://127.0.0.1:5001/api/calculations/api-gravity",
                    json={
                        "specific_gravity": specific_gravity
                    },
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()

                st.metric(
                    "API Gravity",
                    f"{result['api_gravity']:.2f}° API"
                )

            except requests.RequestException as exc:
                st.error(f"Flask API request failed: {exc}")




# ==========================================
# ENGINEERING AI CHAT ASSISTANT
# ==========================================

st.divider()

st.header("Engineering AI Assistant")
st.write(
    "Ask questions about petroleum, mechanical, electrical, "
    "civil, and other engineering topics."
)

# Keep the conversation in Streamlit session state.
if "engineering_ai_messages" not in st.session_state:
    st.session_state.engineering_ai_messages = []

# Display the existing conversation.
for message in st.session_state.engineering_ai_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new question.
question = st.chat_input(
    "Ask Engineering AI a question..."
)

if question:
    previous_history = st.session_state.engineering_ai_messages[-8:].copy()

    # Show the user's question immediately.
    st.session_state.engineering_ai_messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Send the question to the Flask assistant endpoint.
    with st.chat_message("assistant"):
        with st.spinner("Engineering AI is thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:5001/api/assistant",
                    json={
                        "question": question,
                        "conversation_history": previous_history,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                result = response.json()

                # Support common response formats from the assistant.
                if result.get("needs_input"):
                    answer = result.get(
                        "message",
                        "Please provide the missing calculation inputs."
                    )

                elif result.get("success") is False:
                    answer = result.get(
                        "error",
                        result.get("message", "The assistant could not answer.")
                    )

                else:
                    answer = (
                        result.get("answer")
                        or result.get("response")
                        or result.get("message")
                    )

                    if not answer and "pressure_psi" in result:
                        answer = (
                            f"**Hydrostatic Pressure:** "
                            f"{result['pressure_psi']:,.2f} psi\n\n"
                            f"**Formula:** {result.get('formula', 'N/A')}"
                        )

                    elif not answer and "api_gravity" in result:
                        answer = (
                            f"**API Gravity:** "
                            f"{result['api_gravity']:.2f}° API"
                        )

                    if not answer:
                        answer = "The assistant returned no answer text."

                st.markdown(answer)
                st.session_state.engineering_ai_messages.append(
                    {"role": "assistant", "content": str(answer)}
                )

            except requests.RequestException as exc:
                st.error(
                    "Could not contact Engineering AI. "
                    "Confirm that the Flask server is running on port 5001."
                )
                st.caption(str(exc))




# --------------------------------------------------

# FOOTER

# --------------------------------------------------



st.divider()



st.caption(

    "Engineering AI • Educational engineering tools"

)



st.caption(

    "Verify inputs, units, formulas, assumptions, and outputs "

    "before relying on any result."

)


st.caption(

    "BUILT BY EXCELLENT INTELLIGENCE LLC • 2025"

)
