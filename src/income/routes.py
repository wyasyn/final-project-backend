from flask import Blueprint, request, jsonify
from src.models import db, Income
from flask_jwt_extended import jwt_required, get_jwt_identity

income_bp = Blueprint('income', __name__)

# Helper function for error handling
def handle_error(e, message='An error occurred'):
    db.session.rollback()
    return jsonify({'message': message, 'error': str(e)}), 500

# POST - Add Income
@income_bp.route('/', methods=['POST'])
@jwt_required()
def add_income():
    data = request.get_json()
    user_id = get_jwt_identity()

    # Data validation
    if not data.get('amount') or not data.get('date'):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        new_income = Income(
            amount=data['amount'],
            description=data.get('description', ''),
            date=data['date'],
            user_id=user_id
        )

        db.session.add(new_income)
        db.session.commit()
        return jsonify({'message': 'Income added successfully'}), 201

    except Exception as e:
        return handle_error(e, 'Error occurred while adding income')

# GET - Retrieve Income for User (with pagination)
@income_bp.route('/', methods=['GET'])
@jwt_required()
def get_income():
    user_id = get_jwt_identity()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        incomes = Income.query.filter_by(user_id=user_id).paginate(page, per_page, False)
        income_data = [{
            'id': income.id, 'amount': income.amount, 'description': income.description, 'date': income.date
        } for income in incomes.items]

        return jsonify({
            'incomes': income_data, 
            'total_pages': incomes.pages, 
            'current_page': incomes.page
        }), 200
    except Exception as e:
        return handle_error(e, 'Error occurred while retrieving income entries')

# PUT - Update Income (only for the owner)
@income_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_income(id):
    data = request.get_json()
    user_id = get_jwt_identity()

    # Fetch income entry
    income = Income.query.get_or_404(id)

    # Ensure the income belongs to the authenticated user
    if income.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        # Update fields if provided
        income.amount = data.get('amount', income.amount)
        income.description = data.get('description', income.description)
        income.date = data.get('date', income.date)

        db.session.commit()
        return jsonify({'message': 'Income updated successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while updating income')

# DELETE - Delete Income (only for the owner)
@income_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_income(id):
    user_id = get_jwt_identity()

    # Fetch income entry
    income = Income.query.get_or_404(id)

    # Ensure the income belongs to the authenticated user
    if income.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({'message': 'Income deleted successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while deleting income')
