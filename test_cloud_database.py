
from flask_api.cloud_database import test_database_connection

if __name__ == "__main__":
    result = test_database_connection()

    print(result["message"])

    if result["success"]:
        print("Visible rows:", result["rows_visible"])
        print("Cloud database test passed.")
    else:
        print("Error:", result.get("error", "Unknown error"))
        raise SystemExit(1)
