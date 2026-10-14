
from flask import Blueprint, request, jsonify, g
from supabase import create_client

from flask_api.authentication import require_auth
from flask_api.cloud_database import SUPABASE_URL, SUPABASE_KEY

cloud_conversations = Blueprint(
    "cloud_conversations", __name__
)


def user_database():
    # Use the signed-in user's token so Supabase RLS applies.
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(g.access_token)
    return client


@cloud_conversations.get("/api/conversations")
@require_auth
def list_conversations():
    try:
        client = user_database()
        response = (
            client.table("conversations")
            .select("id, title, messages, created_at, updated_at")
            .eq("user_id", g.current_user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return jsonify({
            "success": True,
            "conversations": response.data or []
        })
    except Exception:
        return jsonify({
            "success": False,
            "error": "Could not load cloud conversations."
        }), 500


@cloud_conversations.post("/api/conversations")
@require_auth
def create_conversation():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "New chat")
    messages = data.get("messages", [])

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "success": False, "error": "A title is required."
        }), 400

    if not isinstance(messages, list):
        return jsonify({
            "success": False, "error": "Messages must be a list."
        }), 400

    if len(messages) > 500:
        return jsonify({
            "success": False, "error": "Too many messages."
        }), 400

    # Accept only simple user/assistant messages.
    safe_messages = []
    for message in messages:
        if not isinstance(message, dict):
            return jsonify({
                "success": False, "error": "Invalid message format."
            }), 400

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant") or not isinstance(content, str):
            return jsonify({
                "success": False, "error": "Invalid message fields."
            }), 400

        safe_messages.append({
            "role": role,
            "content": content[:10000]
        })

    try:
        client = user_database()
        response = client.table("conversations").insert({
            "user_id": g.current_user_id,
            "title": title.strip()[:150],
            "messages": safe_messages
        }).execute()

        rows = response.data or []
        if not rows:
            return jsonify({
                "success": False, "error": "Conversation was not created."
            }), 500

        return jsonify({
            "success": True,
            "conversation": rows[0]
        }), 201
    except Exception:
        return jsonify({
            "success": False,
            "error": "Could not save the conversation."
        }), 500


@cloud_conversations.put("/api/conversations/<conversation_id>")
@require_auth
def update_conversation(conversation_id):
    data = request.get_json(silent=True) or {}
    updates = {}

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "success": False, "error": "Invalid title."
            }), 400
        updates["title"] = title.strip()[:150]

    if "messages" in data:
        messages = data["messages"]
        if not isinstance(messages, list) or len(messages) > 500:
            return jsonify({
                "success": False, "error": "Invalid messages list."
            }), 400

        safe_messages = []
        for message in messages:
            if not isinstance(message, dict):
                return jsonify({
                    "success": False, "error": "Invalid message format."
                }), 400

            role = message.get("role")
            content = message.get("content")
            if role not in ("user", "assistant") or not isinstance(content, str):
                return jsonify({
                    "success": False, "error": "Invalid message fields."
                }), 400

            safe_messages.append({
                "role": role, "content": content[:10000]
            })

        updates["messages"] = safe_messages

    if not updates:
        return jsonify({
            "success": False, "error": "No valid updates supplied."
        }), 400

    try:
        client = user_database()
        response = (
            client.table("conversations")
            .update(updates)
            .eq("id", conversation_id)
            .eq("user_id", g.current_user_id)
            .execute()
        )

        rows = response.data or []
        if not rows:
            return jsonify({
                "success": False,
                "error": "Conversation not found or access denied."
            }), 404

        return jsonify({
            "success": True, "conversation": rows[0]
        })
    except Exception:
        return jsonify({
            "success": False,
            "error": "Could not update the conversation."
        }), 500


@cloud_conversations.delete("/api/conversations/<conversation_id>")
@require_auth
def delete_conversation(conversation_id):
    try:
        client = user_database()
        response = (
            client.table("conversations")
            .delete()
            .eq("id", conversation_id)
            .eq("user_id", g.current_user_id)
            .execute()
        )

        if not response.data:
            return jsonify({
                "success": False,
                "error": "Conversation not found or access denied."
            }), 404

        return jsonify({"success": True})
    except Exception:
        return jsonify({
            "success": False,
            "error": "Could not delete the conversation."
        }), 500
