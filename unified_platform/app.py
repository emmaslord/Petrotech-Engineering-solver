
from flask import Flask, render_template

app = Flask(__name__)

ENGINEERING_MODULES = [
    {
        "name": "PetroTech Engineering Solver",
        "category": "Petroleum Engineering",
        "description": (
            "Drilling calculations, mud hydraulics, "
            "well pressure and pump calculations."
        ),
        "url": "http://127.0.0.1:8501",
        "icon": "🛢️",
        "status": "Independent application",
    },
    {
        "name": "General Engineering Technology Solver",
        "category": "Multi-discipline Engineering",
        "description": (
            "Mechanical, electrical, civil, "
            "petroleum and general calculations."
        ),
        "url": "http://127.0.0.1:5000",
        "icon": "⚙️",
        "status": "Independent application",
    },
]


@app.route("/")
def home():
    return render_template(
        "index.html",
        modules=ENGINEERING_MODULES,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
    )
