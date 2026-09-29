from flask import Flask, jsonify
from .config import Config
from .extensions import db, ma, init_extensions
from .routes.auth import auth_bp
from .routes.boards import boards_bp
from .routes.tasks import tasks_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_extensions(app)
    with app.app_context():
        db.create_all()

    @app.errorhandler(400)
    @app.errorhandler(422)
    def handle_validation_error(error):
        return jsonify({
            "error": "Validation Error",
            "details": str(error.description),
        }), error.code

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(boards_bp)
    app.register_blueprint(tasks_bp)

    return app