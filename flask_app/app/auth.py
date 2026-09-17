# flask_app/app/auth.py
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from passlib.context import CryptContext
from .extensions import db
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(username):
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing authorization header"}), 401
            
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            username = payload['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
        current_user = User.query.filter_by(username=username).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 401
            
        # Inject user into route context
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    return decorated