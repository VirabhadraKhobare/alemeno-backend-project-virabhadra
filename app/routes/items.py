from flask import Blueprint, jsonify, request
from ..models import Item
from ..extensions import db

bp = Blueprint('items', __name__)

@bp.route('/', methods=['GET'])
def list_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items]), 200

@bp.route('/', methods=['POST'])
def create_item():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error':'name required'}), 400
    item = Item(name=name, description=data.get('description'))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201
