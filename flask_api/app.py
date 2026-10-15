"""Flask API for Engineering AI.

Run from the project root with:
    python -m flask --app flask_api.app run --host 127.0.0.1 --port 5001
"""

import json
import sys
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from flask import (
    Flask,
    Response,
    jsonify,
    request,
    send_from_directory,
    stream_with_context,
)
from werkzeug.utils import secure_filename

# Make the project root importable before importing project modules.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask_api.admin_routes import admin_routes
from flask_api.authentication import require_auth
from flask_api.cloud_conversations import cloud_conversations
from flask_api.cloud_database import SUPABASE_KEY, SUPABASE_URL
from petrotech_ai.assistant import (
    answer_question,
    normalize_ai_mode,
    stream_answer_question,
)

# File extraction dependencies.
import easyocr
import numpy as np
from PIL import Image
from pypdf import PdfReader


app = Flask(__name__)

# Up to five 5 MB files, plus multipart/form-data overhead.
app.config["MAX_CONTENT_LENGTH"] = 26 * 1024 * 1024

ASSETS_DIR = PROJECT_ROOT / "engineering_ai_web" / "assets"
ALLOWED_ORIGINS = {
    "http://127.0.0.1:5501",
    "http://localhost:5501",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
}

app.register_blueprint(cloud_conversations)
app.register_blueprint(admin_routes)


@lru_cache(maxsize=1)
def get_ocr_reader():
    """Initialize EasyOCR once and reuse it for later image uploads."""
    return easyocr.Reader(["en"], gpu=False)


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({
        "success": False,
        "error": "The upload request is too large. Upload up to 5 files, each no larger than 5 MB.",
    }), 413


@app.get("/assets/<path:filename>")
def serve_assets(filename):
    """Serve frontend assets from engineering_ai_web/assets."""
    return send_from_directory(ASSETS_DIR, filename)


@app.get("/")
def index():
    return jsonify({
        "success": True,
        "message": "Engineering AI API running",
    })


@app.get("/health")
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
    })


@app.post("/api/upload")
@require_auth
def upload_files():
    """Extract text from supported image, PDF, TXT, and CSV attachments."""
    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "success": False,
            "error": "Please attach at least one file.",
        }), 400

    if len(files) > 5:
        return jsonify({
            "success": False,
            "error": "You can upload a maximum of 5 files at once.",
        }), 400

    results = []
    total_chars = 0
    max_file_bytes = 5 * 1024 * 1024
    max_total_chars = 20000
    image_extensions = {"png", "jpg", "jpeg", "webp", "bmp"}
    text_extensions = {"txt", "csv"}
    supported_extensions = image_extensions | text_extensions | {"pdf"}

    for uploaded_file in files:
        original_name = (uploaded_file.filename or "").strip()
        filename = Path(original_name.replace("\\", "/")).name

        if not filename:
            return jsonify({
                "success": False,
                "error": "A file has no valid filename.",
            }), 400

        # Validate using the extension, not the browser-supplied MIME type.
        safe_name = secure_filename(filename) or "attachment"
        suffix = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""

        if suffix not in supported_extensions:
            return jsonify({
                "success": False,
                "error": (
                    f"Unsupported file type: {filename}. "
                    "Use PNG, JPG, JPEG, WEBP, BMP, PDF, TXT, or CSV."
                ),
            }), 400

        # Read at most 5 MB plus one byte to detect oversized files.
        raw = uploaded_file.stream.read(max_file_bytes + 1)

        if not raw:
            return jsonify({
                "success": False,
                "error": f"{filename} is empty.",
            }), 400

        if len(raw) > max_file_bytes:
            return jsonify({
                "success": False,
                "error": f"{filename} exceeds the 5 MB per-file limit.",
            }), 413

        try:
            if suffix in text_extensions:
                extracted = raw.decode("utf-8-sig", errors="replace")

            elif suffix == "pdf":
                reader = PdfReader(BytesIO(raw))

                if reader.is_encrypted:
                    return jsonify({
                        "success": False,
                        "error": f"{filename} is password-protected.",
                    }), 400

                extracted = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages[:50]
                )

                if not extracted.strip():
                    extracted = (
                        "No selectable text was found in this PDF. "
                        "It may be scanned; try uploading its pages as images."
                    )

            else:
                # Verify the image before OCR to reject invalid image data.
                with Image.open(BytesIO(raw)) as image:
                    if image.width * image.height > 20_000_000:
                        return jsonify({
                            "success": False,
                            "error": f"{filename} has too many pixels.",
                        }), 400
                    image.verify()

                with Image.open(BytesIO(raw)) as image:
                    image_array = np.array(image.convert("RGB"))

                text_lines = get_ocr_reader().readtext(
                    image_array,
                    detail=0,
                )
                extracted = "\n".join(str(line) for line in text_lines)

                if not extracted.strip():
                    extracted = "No readable text was detected in this image."

        except Exception:
            app.logger.exception("File extraction failed for %s", safe_name)
            return jsonify({
                "success": False,
                "error": (
                    f"Could not read {filename}. "
                    "Check that the file is valid and try again."
                ),
            }), 400

        remaining = max_total_chars - total_chars
        extracted = extracted[:max(0, remaining)]
        total_chars += len(extracted)

        results.append({
            "name": filename[:200],
            "text": extracted,
        })

    combined_text = "\n\n".join(
        f"File: {item['name']}\n{item['text']}"
        for item in results
    )

    return jsonify({
        "success": True,
        "files": results,
        "combined_text": combined_text,
    })


@app.get("/api/config")
def public_config():
    """Return public Supabase client configuration (never a service-role key)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({
            "success": False,
            "error": "Supabase configuration is missing.",
        }), 503

    return jsonify({
        "success": True,
        "supabaseUrl": SUPABASE_URL,
        "supabaseKey": SUPABASE_KEY,
    })


@app.after_request
def add_cors_headers(response):
    """Allow the local frontend to call this API."""
    origin = request.headers.get("Origin")

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Max-Age"] = "600"

    return response


def get_safe_history(history):
    """Return only valid, recent user/assistant messages."""
    if not isinstance(history, list):
        return None

    safe_history = []
    for message in history[-8:]:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            continue

        if isinstance(content, str) and content.strip():
            safe_history.append({
                "role": role,
                "content": content.strip()[:2000],
            })

    return safe_history


def get_request_data():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


@app.post("/api/assistant")
def assistant_endpoint():
    data = get_request_data()
    question = data.get("question", "")
    history = data.get("conversation_history", [])
    safe_history = get_safe_history(history)

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "success": False,
            "error": "Please provide a question.",
        }), 400

    if safe_history is None:
        return jsonify({
            "success": False,
            "error": "Conversation history must be a list.",
        }), 400

    try:
        mode = normalize_ai_mode(data.get("mode", "general_engineering"))
        app.logger.info("Assistant request received: %r", question[:250])

        result = answer_question(
            question.strip(),
            conversation_history=safe_history,
            mode=mode,
        )

        if not isinstance(result, dict):
            app.logger.error("answer_question returned %s, expected dict", type(result).__name__)
            return jsonify({
                "success": False,
                "error": "Unexpected assistant response.",
            }), 500

        # Preserve calculation-specific errors returned by the solver.
        status_code = 400 if result.get("success") is False and result.get("error") else 200
        return jsonify(result), status_code

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 400
    except Exception:
        app.logger.exception("Engineering AI assistant request failed")
        return jsonify({
            "success": False,
            "error": "The assistant could not process this request.",
        }), 500


@app.post("/api/assistant/stream")
def assistant_stream_endpoint():
    data = get_request_data()
    question = data.get("question", "")
    history = data.get("conversation_history", [])
    safe_history = get_safe_history(history)

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "success": False,
            "error": "Please provide a question.",
        }), 400

    if safe_history is None:
        return jsonify({
            "success": False,
            "error": "Conversation history must be a list.",
        }), 400

    try:
        mode = normalize_ai_mode(data.get("mode", "general_engineering"))
    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 400

    def generate():
        try:
            for chunk in stream_answer_question(
                question.strip(),
                conversation_history=safe_history,
                mode=mode,
            ):
                yield "data: " + json.dumps({"chunk": str(chunk)}) + "\n\n"

            yield "data: " + json.dumps({"done": True}) + "\n\n"

        except Exception:
            app.logger.exception("Engineering AI streaming request failed")
            yield "data: " + json.dumps({
                "error": "The assistant could not complete the response.",
            }) + "\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
