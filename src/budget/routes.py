from flask import Blueprint, request, jsonify
from src.models import db, Budget
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

# Helper function to handle user identity
def get_user_id():
    return get_jwt_identity()

# Route to add a new budget
@budget_bp.route('/', methods=['POST'])
@jwt_required()
def add_budget():
    data = request.get_json()

    # Validate input data
    required_fields = ['category', 'amount', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        raise BadRequest(f"Missing required fields: {', '.join([field for field in required_fields if field not in data])}")

    try:
        # Validate date formats
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    except ValueError:
        raise BadRequest("Invalid date format. Expected format: YYYY-MM-DD")

    user_id = get_user_id()

    new_budget = Budget(
        category=data['category'],
        amount=data['amount'],
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )

    db.session.add(new_budget)
    try:
        db.session.commit()
        return jsonify({'message': 'Budget added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f"Error adding budget: {str(e)}"}), 500

# Route to get all budgets for the current user
@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    user_id = get_user_id()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    if not budgets:
        return jsonify({'message': 'No budgets found for the user.'}), 404

    budget_data = [{
        'id': budget.id,
        'category': budget.category,
        'amount': budget.amount,
        'start_date': budget.start_date,
        'end_date': budget.end_date
    } for budget in budgets]

    return jsonify({'budgets': budget_data}), 200

# Route to update an existing budget
@budget_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_budget(id):
    data = request.get_json()

    budget = Budget.query.get_or_404(id)

    # Ensure the budget belongs to the current user
    if budget.user_id != get_user_id():
        return jsonify({'message': 'Unauthorized access to this budget'}), 403

    # Validate input data
    if 'category' in data:
        budget.category = data['category']
    if 'amount' in data:
        budget.amount = data['amount']
    if 'start_date' in data:
        try:
            budget.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Invalid start date format. Expected format: YYYY-MM-DD'}), 400
    if 'end_date' in data:
        try:
            budget.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Invalid end date format. Expected format: YYYY-MM-DD'}), 400

    try:
        db.session.commit()
        return jsonify({'message': 'Budget updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f"Error updating budget: {str(e)}"}), 500

# Route to delete an existing budget
@budget_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_budget(id):
    budget = Budget.query.get_or_404(id)

    # Ensure the budget belongs to the current user
    if budget.user_id != get_user_id():
        return jsonify({'message': 'Unauthorized access to this budget'}), 403

    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': 'Budget deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f"Error deleting budget: {str(e)}"}), 500
