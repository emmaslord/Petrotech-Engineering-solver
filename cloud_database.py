
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

# Load the .env file from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_client = None


def get_supabase_client() -> Client:
    """Create and reuse the Supabase client."""
    global _client

    if _client is not None:
        return _client

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase configuration is missing. "
            "Check SUPABASE_URL and SUPABASE_KEY in your .env file."
        )

    _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def test_database_connection() -> dict:
    """Test access to the conversations table."""
    try:
        client = get_supabase_client()

        # With row-level security enabled, unauthenticated access
        # should not reveal another user's conversations.
        response = (
            client.table("conversations")
            .select("id")
            .limit(1)
            .execute()
        )

        return {
            "success": True,
            "message": "Supabase connection succeeded.",
            "rows_visible": len(response.data or []),
        }

    except Exception as exc:
        # Do not return credentials or environment variable values.
        return {
            "success": False,
            "message": "Supabase connection test failed.",
            "error": str(exc),
        }
