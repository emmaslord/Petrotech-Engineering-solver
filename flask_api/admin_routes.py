
import os

from flask import Blueprint, jsonify, g
from supabase import create_client

from flask_api.cloud_database import SUPABASE_URL
from flask import g
from flask_api.authentication import require_auth
from flask_api.admin_auth import require_admin
from flask_api.activity_logger import log_system_activity
from flask_api.authentication import require_auth
from flask_api.admin_auth import require_admin


admin_routes = Blueprint("admin_routes", __name__)


def get_admin_client():
    """Create the server-side Supabase admin client when configured."""
    admin_key = os.getenv("SUPABASE_ADMIN_KEY", "").strip()

    if not SUPABASE_URL or not admin_key:
        return None

    return create_client(SUPABASE_URL, admin_key)


@admin_routes.get("/api/admin/check")
@require_auth
@require_admin
def admin_access_check():
    """Confirm that the authenticated user has admin permission."""
    log_system_activity(
        "admin_access_verified",
        actor_user_id=g.current_user_id,
        metadata={
            "route": "/api/admin/check",
            "status": 200,
        },
    )

    return jsonify({
        "success": True,
        "message": "Administrator access verified.",
    }), 200


@admin_routes.get("/api/admin/users")
@require_auth
@require_admin
def list_admin_users():
    """List registered users for authorized administrators only."""
    client = get_admin_client()

    if client is None:
        return jsonify({
            "success": False,
            "error": "Admin database access is not configured.",
        }), 503

    try:
        result = client.auth.admin.list_users(page=1, per_page=50)
        users = getattr(result, "users", result)

        log_system_activity(
            "admin_users_viewed",
            actor_user_id=g.current_user_id,
            metadata={
                "route": "/api/admin/users",
                "status": 200,
            },
        )

        return jsonify({
            "success": True,
            "count": len(users),
            "users": [
                {
                    "id": str(user.id),
                    "email": getattr(user, "email", None),
                    "created_at": getattr(user, "created_at", None),
                    "last_sign_in_at": getattr(
                        user, "last_sign_in_at", None
                    ),
                    "email_confirmed_at": getattr(
                        user, "email_confirmed_at", None
                    ),
                }
                for user in users
            ],
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Unable to retrieve registered users.",
        }), 502


@admin_routes.get("/api/admin/health")
@require_auth
@require_admin
def admin_system_health():
    """Return safe service health information to verified administrators."""
    health_status = {
        "success": True,
        "api": "online",
        "database": "unknown",
    }

    client = get_admin_client()

    if client is None:
        health_status["database"] = "not_configured"
    else:
        try:
            client.auth.admin.list_users(page=1, per_page=1)
            health_status["database"] = "online"
        except Exception:
            health_status["database"] = "unavailable"

    log_system_activity(
        "system_health_checked",
        actor_user_id=g.current_user_id,
        metadata={
            "route": "/api/admin/health",
            "status": health_status["database"],
        },
    )

    return jsonify(health_status), 200


@admin_routes.get("/api/admin/activity")
@require_auth
@require_admin
def list_system_activity():
    """Return recent system activity to verified administrators only."""
    client = get_admin_client()

    if client is None:
        return jsonify({
            "success": False,
            "error": "Activity logging service is not configured.",
        }), 503

    try:
        result = (
            client.table("system_activity_logs")
            .select(
                "id, actor_user_id, event_type, metadata, created_at"
            )
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        activity = result.data or []

        return jsonify({
            "success": True,
            "count": len(activity),
            "activity": activity,
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Unable to retrieve system activity.",
        }), 502