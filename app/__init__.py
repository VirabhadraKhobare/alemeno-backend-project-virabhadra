import os
from .extensions import db


def create_app():
    """Create and configure the Flask application.

    NOTE: delay importing Flask until this function runs so the package can be
    imported in lightweight environments (for example Streamlit Cloud) that
    don't have Flask installed. Importing Flask at module import time caused
    ModuleNotFoundError for Streamlit deployments.
    """
    from flask import Flask

    app = Flask(__name__, instance_relative_config=False)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Blueprints
    from .routes.health import bp as health_bp
    from .routes.items import bp as items_bp
    from .routes.ml import bp as ml_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(items_bp, url_prefix='/api/v1/items')
    app.register_blueprint(ml_bp, url_prefix='/api/v1/ml')

    # Create DB tables if needed (simple)
    with app.app_context():
        db.create_all()

    return app
