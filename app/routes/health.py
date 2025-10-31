try:
    from flask import Blueprint, jsonify
except Exception:  # pragma: no cover - import may fail in Streamlit runtime
    # Provide fallbacks so importing this module doesn't crash when Flask
    # isn't installed (Streamlit Cloud minimal environment). These fallbacks
    # won't be used at runtime by Flask but allow static import inside
    # Streamlit front-ends.
    Blueprint = None  # type: ignore
    def jsonify(x):
        return x


bp = Blueprint("health", __name__) if Blueprint else None


def health():
    return jsonify({"status": "ok"}), 200
