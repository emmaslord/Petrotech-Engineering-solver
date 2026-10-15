
import os
from functools import wraps

from flask import jsonify, g


def require_admin(view_function):
    """Require a verified Supabase user ID on the server-side allowlist."""

    @wraps(view_function)
    def decorated(*args, **kwargs):
        # require_auth must run before this decorator.
        user_id = getattr(g, "current_user_id", None)

        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        admin_ids = {
            item.strip()
            for item in os.getenv("ADMIN_USER_IDS", "").split(",")
            if item.strip()
        }

        if not admin_ids:
            return jsonify({
                "success": False,
                "error": "Administrator access is not configured."
            }), 503

        if str(user_id) not in admin_ids:
            return jsonify({
                "success": False,
                "error": "Administrator permission required."
            }), 403

        return view_function(*args, **kwargs)

    return decorated
