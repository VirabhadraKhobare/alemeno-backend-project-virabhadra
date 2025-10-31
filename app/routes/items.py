try:
    from flask import Blueprint, jsonify, request
except Exception:  # pragma: no cover - import may fail in Streamlit runtime
    Blueprint = None  # type: ignore
    def jsonify(x):
        return x
    request = None  # type: ignore

from ..models import Item
from ..extensions import db


bp = Blueprint("items", __name__) if Blueprint else None


def list_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items]), 200


def create_item():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    if len(name) > 120:
        return jsonify({"error": "name too long (max 120)"}), 400

    item = Item(name=name, description=data.get("description"))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


def get_item(item_id: int):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item.to_dict()), 200


def delete_item(item_id: int):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": item_id}), 200
