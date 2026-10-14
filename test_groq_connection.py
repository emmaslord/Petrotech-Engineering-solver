
import streamlit as st
from ai_fallback import ask_groq

st.title("PetroTech — Groq Connection Test")

st.write("Test the external AI without changing the main application.")

question = st.text_input(
    "Test question",
    value="Explain hydrostatic pressure in simple terms."
)

if st.button("Test Groq"):
    with st.spinner("Contacting Groq..."):
        result = ask_groq(question)

    if result["success"]:
        st.success("Groq connection successful!")
        st.write(result["answer"])
    else:
        st.error(result["message"])
