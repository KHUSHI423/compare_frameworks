from flask import Flask
from .config import Config
from .extensions import db, ma, init_extensions

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    init_extensions(app)
    
    #APP FACTORY
    
    # Register blueprints here later
    # from .routes.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app