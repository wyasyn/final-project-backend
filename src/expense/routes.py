from flask import Blueprint, request, jsonify
from src.models import db, Expense
from flask_jwt_extended import jwt_required, get_jwt_identity

expense_bp = Blueprint('expense', __name__)

# Helper function for error handling
def handle_error(e, message='An error occurred'):
    db.session.rollback()
    return jsonify({'message': message, 'error': str(e)}), 500

# POST - Add Expense
@expense_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    user_id = get_jwt_identity()

    # Data validation
    if not data.get('amount') or not data.get('date'):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        new_expense = Expense(
            amount=data['amount'],
            description=data.get('description', ''),
            date=data['date'],
            category=data.get('category', 'General'),
            user_id=user_id
        )

        db.session.add(new_expense)
        db.session.commit()
        return jsonify({'message': 'Expense added successfully'}), 201

    except Exception as e:
        return handle_error(e, 'Error occurred while adding expense')

# GET - Retrieve Expenses for User (with pagination)
@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        expenses = Expense.query.filter_by(user_id=user_id).paginate(page, per_page, False)
        expense_data = [{
            'id': expense.id,
            'amount': expense.amount,
            'description': expense.description,
            'date': expense.date,
            'category': expense.category
        } for expense in expenses.items]

        return jsonify({
            'expenses': expense_data,
            'total_pages': expenses.pages,
            'current_page': expenses.page
        }), 200
    except Exception as e:
        return handle_error(e, 'Error occurred while retrieving expenses')

# PUT - Update Expense (only for the owner)
@expense_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    data = request.get_json()
    user_id = get_jwt_identity()

    # Fetch expense entry
    expense = Expense.query.get_or_404(id)

    # Ensure the expense belongs to the authenticated user
    if expense.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        # Update fields if provided
        expense.amount = data.get('amount', expense.amount)
        expense.description = data.get('description', expense.description)
        expense.date = data.get('date', expense.date)
        expense.category = data.get('category', expense.category)

        db.session.commit()
        return jsonify({'message': 'Expense updated successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while updating expense')

# DELETE - Delete Expense (only for the owner)
@expense_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    user_id = get_jwt_identity()

    # Fetch expense entry
    expense = Expense.query.get_or_404(id)

    # Ensure the expense belongs to the authenticated user
    if expense.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while deleting expense')
