from flask import Blueprint, request, jsonify
from ..ml.integration import summarize_text


bp = Blueprint("ml", __name__)


@bp.route("/summarize", methods=["POST"])
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
