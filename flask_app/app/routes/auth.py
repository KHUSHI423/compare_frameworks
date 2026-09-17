# flask_app/app/routes/auth.py
from flask import Blueprint, request, jsonify
from .auth import get_password_hash, create_access_token, verify_password, jwt_required
from ..extensions import db
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({"error": "Missing fields"}), 400
        
    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({"error": "Username or email already exists"}), 409
        
    user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=get_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not verify_password(data.get('password', ''), user.hashed_password):
        return jsonify({"error": "Incorrect credentials"}), 401
        
    token = create_access_token(user.username)
    return jsonify({"access_token": token, "token_type": "bearer"})

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def me(current_user=None):
    return jsonify({"id": current_user.id, "username": current_user.username, "email": current_user.email})