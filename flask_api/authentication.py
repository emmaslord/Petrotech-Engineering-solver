
from functools import wraps

from flask import request, jsonify, g
from supabase import create_client

from flask_api.cloud_database import SUPABASE_URL, SUPABASE_KEY


def require_auth(view_function):
    @wraps(view_function)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        token = authorization[7:].strip()

        if not token:
            return jsonify({
                "success": False,
                "error": "Missing access token."
            }), 401

        if not SUPABASE_URL or not SUPABASE_KEY:
            return jsonify({
                "success": False,
                "error": "Authentication service is not configured."
            }), 503

        try:
            # Validate the token with Supabase Auth.
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = client.auth.get_user(token)
            user = response.user

            if not user or not user.id:
                raise ValueError("No authenticated user.")

            # Store identity verified by Supabase, not browser input.
            g.current_user_id = str(user.id)
            g.access_token = token

        except Exception:
            return jsonify({
                "success": False,
                "error": "Invalid or expired access token. Please sign in again."
            }), 401

        return view_function(*args, **kwargs)

    return decorated
