from flask import request, jsonify, url_for, Blueprint, make_response, current_app
from src import mail, db
from src.models import User
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, set_access_cookies
)
from datetime import datetime, timedelta


user_bp = Blueprint('user_bp', __name__)

def user_exists(identifier):
    """Helper function to check if a user exists based on email or username."""
    return User.query.filter((User.username == identifier) | (User.email == identifier)).first()

@user_bp.route('/add-user', methods=['POST'])
def add_user():
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Check if the email or username already exists
    if user_exists(data['email']) or user_exists(data['username']):
        return jsonify({'error': 'Email or Username already exists'}), 400

    try:
        # Create a new user and set the password using the model's set_password method
        new_user = User(
            email=data['email'],
            username=data['username'],
            date_of_birth=datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date() if 'date_of_birth' in data else None,
            **{k: data.get(k) for k in ['first_name', 'last_name', 'middle_name', 'image_url', 'career', 'phone_number']}
        )
        new_user.set_password(data['password'])  
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(days=7))
        response = make_response(jsonify({'message': 'User added and logged in successfully'}), 201)
        set_access_cookies(response, access_token)
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add user', 'details': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'error': 'Identifier and password are required'}), 400

    user = user_exists(identifier)

    if user and user.check_password(password): 
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7))
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        set_access_cookies(response, access_token)
        return response

    return jsonify({'error': 'Invalid identifier or password'}), 401



@user_bp.route('/edit-user', methods=['PUT'])
@jwt_required()
def edit_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    for field in ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'image_url', 'career', 'phone_number']:
        if field in data:
            setattr(user, field, data[field])

    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@user_bp.route('/delete-user', methods=['DELETE'])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the user"}), 500

@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        try:
            token = user.get_reset_password_token()  # Using model's method
            reset_url = url_for('user_bp.reset_password', token=token, _external=True)

            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f'Click the link to reset your password: {reset_url}'
            mail.send(msg)
        except Exception as e:
            return jsonify({'message': 'Failed to send email', 'details': str(e)}), 500

    return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200

@user_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = User.verify_reset_password_token(token)  # Using model's method
    except Exception:
        return jsonify({'error': 'Invalid or expired token'}), 400

    data = request.get_json()
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'Password is required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.set_password(new_password)  # Using model's method
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    return jsonify({'error': 'User not found'}), 404



@user_bp.route('/get-user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200


@user_bp.route('/get-users', methods=['GET'])
@jwt_required()
def get_users():
    """Get a list of all users."""
    try:
        users = User.query.all()
        users_data = [user.to_dict() for user in users]
        return jsonify(users_data), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch users: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


