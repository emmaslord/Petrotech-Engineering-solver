
import requests

ENGINEERING_API_URL = "http://127.0.0.1:5002"


def check_api_health():
    """Check whether the Engineering Suite API is responding."""
    response = requests.get(
        f"{ENGINEERING_API_URL}/api/health",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def get_petrotech_calculations():
    """Retrieve the PetroTech calculations exposed by Flask."""
    response = requests.get(
        f"{ENGINEERING_API_URL}/api/petrotech/calculations",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def calculate_petrotech(calculation, inputs):
    """Send a PetroTech calculation request to the Flask API."""
    response = requests.post(
        f"{ENGINEERING_API_URL}/api/petrotech/calculate",
        json={
            "calculation": calculation,
            "inputs": inputs,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
