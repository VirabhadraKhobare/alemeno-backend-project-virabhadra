try:
    from flask import Blueprint, request, jsonify
except Exception:  # pragma: no cover - import may fail in Streamlit runtime
    Blueprint = None  # type: ignore
    def jsonify(x):
        return x
    request = None  # type: ignore

from ..ml.integration import summarize_text


bp = Blueprint("ml", __name__) if Blueprint else None


def summarize():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text required"}), 400

    try:
        result = summarize_text(text)
        return jsonify({"summary": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
