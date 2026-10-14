
import streamlit as st
from groq import Groq

try:
    key = st.secrets.get("GROQ_API_KEY")

    if not isinstance(key, str) or not key.strip():
        print("CONFIG ERROR: GROQ_API_KEY is missing or empty.")
    else:
        print("PASS: Streamlit found the configured key.")

        client = Groq(api_key=key)
        client.models.list()

        print("SUCCESS: Groq accepted the key and the API connection works.")

except FileNotFoundError:
    print("ERROR: Streamlit could not find secrets.toml.")
except Exception as exc:
    print("CONNECTION TEST FAILED:", type(exc).__name__)
    print("Details:", str(exc)[:300])
