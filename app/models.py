from .extensions import db


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}
