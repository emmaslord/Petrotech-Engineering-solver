
"""Engineering AI analytics event endpoint."""

import os
import re
from uuid import UUID

from flask import Blueprint, jsonify, request
from supabase import create_client

from flask_api.cloud_database import SUPABASE_URL
from flask_api.authentication import require_auth
from flask_api.admin_auth import require_admin
analytics_routes = Blueprint("analytics_routes", __name__)

ALLOWED_EVENTS = {
    "page_view",
    "session_start",
    "feature_used",
}

ALLOWED_DEVICES = {
    "mobile",
    "desktop",
    "tablet",
    "unknown",
}


@analytics_routes.post("/api/analytics/event")
def record_analytics_event():
    """Validate and store a minimal analytics event."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A JSON event is required.",
        }), 400

    event_name = data.get("event_name")
    session_id = data.get("session_id")
    page_path = data.get("page_path", "/")
    device_type = data.get("device_type", "unknown")

    if event_name not in ALLOWED_EVENTS:
        return jsonify({
            "success": False,
            "error": "Unsupported event type.",
        }), 400

    try:
        session_id = str(UUID(str(session_id)))
    except (ValueError, TypeError, AttributeError):
        return jsonify({
            "success": False,
            "error": "Invalid session ID.",
        }), 400

    if not isinstance(page_path, str) or not re.fullmatch(
        r"/[A-Za-z0-9/_-]{0,150}", page_path
    ):
        return jsonify({
            "success": False,
            "error": "Invalid page path.",
        }), 400

    if device_type not in ALLOWED_DEVICES:
        return jsonify({
            "success": False,
            "error": "Invalid device type.",
        }), 400

    admin_key = os.getenv("SUPABASE_ADMIN_KEY", "").strip()

    if not SUPABASE_URL or not admin_key:
        return jsonify({
            "success": False,
            "error": "Analytics storage is not configured.",
        }), 503

    try:
        client = create_client(SUPABASE_URL, admin_key)

        client.table("analytics_events").insert({
            "event_name": event_name,
            "session_id": session_id,
            "page_path": page_path,
            "device_type": device_type,
        }).execute()

        return jsonify({"success": True}), 201

    except Exception:
        # Do not expose credentials or database error details.
        return jsonify({
            "success": False,
            "error": "Could not record analytics event.",
        }), 502



@analytics_routes.get("/api/analytics/summary")
@require_auth
@require_admin
def analytics_summary():
    """Return analytics statistics for authorized administrators."""

    admin_key = os.getenv("SUPABASE_ADMIN_KEY", "").strip()

    if not SUPABASE_URL or not admin_key:
        return jsonify({
            "success": False,
            "error": "Analytics storage is not configured.",
        }), 503

    try:
        client = create_client(SUPABASE_URL, admin_key)

        result = (
            client.table("analytics_events")
            .select(
                "event_name,session_id,page_path,device_type,created_at"
            )
            .order("created_at", desc=True)
            .limit(5000)
            .execute()
        )

        events = result.data or []

        page_views = [
            event for event in events
            if event.get("event_name") == "page_view"
        ]

        sessions = {
            event["session_id"]
            for event in events
            if event.get("session_id")
        }

        popular_pages = {}
        devices = {}

        for event in page_views:
            path = event.get("page_path", "/")
            popular_pages[path] = popular_pages.get(path, 0) + 1

        for event in events:
            device = event.get("device_type", "unknown")
            devices[device] = devices.get(device, 0) + 1

        return jsonify({
            "success": True,
            "total_events": len(events),
            "unique_sessions": len(sessions),
            "page_views": len(page_views),
            "popular_pages": [
                {"page": page, "views": count}
                for page, count in sorted(
                    popular_pages.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[:10]
            ],
            "devices": devices,
            "note": "Statistics cover at most the latest 5000 events.",
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Could not retrieve analytics summary.",
        }), 502
