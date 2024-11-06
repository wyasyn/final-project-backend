from flask import request, jsonify, url_for, Blueprint, make_response
from src import create_app
from src.models import db, User
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from datetime import datetime, timedelta


app = create_app()



# Token Serializer
serializer = URLSafeTimedSerializer(app.secret_key)
mail = Mail(app)

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/add-user', methods=['POST'])
def add_user():
    data = request.get_json()

    # Validate required fields and uniqueness
    required_fields = ['email', 'username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Invalid Email or Password'}), 400

    # Convert date_of_birth to Python date object if provided
    try:
        date_of_birth = None
        if 'date_of_birth' in data:
            date_of_birth = datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD for date_of_birth.'}), 400

    # Optional fields and user creation
    try:
        new_user = User(
            email=data['email'],
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            date_of_birth=date_of_birth,
            **{k: data.get(k) for k in ['first_name', 'last_name', 'middle_name', 'image_url', 'career', 'phone_number']}
        )
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the user by creating a JWT token
        access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(days=7))
        
        # Set token as HTTP-only cookie
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

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7))
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        set_access_cookies(response, access_token)
        print(access_token) 
        return response

    return jsonify({'error': 'Invalid identifier or password'}), 401



@user_bp.route('/get-user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'middle_name': user.middle_name,
        'date_of_birth': user.date_of_birth,
        'image_url': user.image_url,
        'career': user.career,
        'phone_number': user.phone_number,
        'email': user.email,
        'username': user.username,
        'created_at': user.created_at
    }

    return jsonify({'user': user_data}), 200

@user_bp.route('/get-user', methods=['PUT'])
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
        token = serializer.dumps(user.email, salt='password-reset-salt')
        reset_url = url_for('reset_password', token=token, _external=True)
        msg = Message("Password Reset Request", recipients=[email])
        msg.body = f'Click the link to reset your password: {reset_url}'
        mail.send(msg)

    return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200

@user_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return jsonify({'error': 'Invalid or expired token'}), 400

    data = request.get_json()
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'Password is required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@user_bp.route('/get-users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Retrieve a list of all users."""
    users = User.query.all()
    
    # Serialize users data to JSON format
    users_data = [
        {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'middle_name': user.middle_name,
            'date_of_birth': user.date_of_birth,
            'image_url': user.image_url,
            'career': user.career,
            'phone_number': user.phone_number,
            'email': user.email,
            'username': user.username,
            'created_at': user.created_at
        }
        for user in users
    ]

    return jsonify({'users': users_data}), 200

