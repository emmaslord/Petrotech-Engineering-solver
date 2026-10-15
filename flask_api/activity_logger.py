
"""Secure helper for recording system activity."""

import logging
import os
from uuid import UUID

from supabase import create_client

logger = logging.getLogger(__name__)

ALLOWED_EVENTS = {
    "admin_access_verified",
    "admin_users_viewed",
    "system_health_checked",
}


def log_system_activity(
    event_type: str,
    actor_user_id: str | None = None,
    metadata: dict | None = None,
) -> bool:
    """Record a minimal operational event using server-side credentials."""

    if event_type not in ALLOWED_EVENTS:
        logger.warning("Rejected unsupported activity event type.")
        return False

    admin_key = os.getenv("SUPABASE_ADMIN_KEY", "").strip()

    from flask_api.cloud_database import SUPABASE_URL

    if not SUPABASE_URL or not admin_key:
        logger.error("Activity logging is not configured.")
        return False

    if actor_user_id is not None:
        try:
            actor_user_id = str(UUID(actor_user_id))
        except (ValueError, TypeError, AttributeError):
            logger.warning("Rejected invalid activity actor ID.")
            return False

    # Only accept a small, fixed set of safe metadata fields.
    safe_metadata = {}
    if isinstance(metadata, dict):
        for key in ("route", "status"):
            value = metadata.get(key)
            if isinstance(value, (str, int)) and not isinstance(value, bool):
                safe_metadata[key] = value

    try:
        client = create_client(SUPABASE_URL, admin_key)

        client.table("system_activity_logs").insert({
            "actor_user_id": actor_user_id,
            "event_type": event_type,
            "metadata": safe_metadata,
        }).execute()

        return True

    except Exception:
        # Never log credentials, tokens, request bodies, or exception details.
        logger.error("Failed to write a system activity event.")
        return False
