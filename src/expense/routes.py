from flask import Blueprint, request, jsonify
from src.models import db, Expense
from flask_jwt_extended import jwt_required, get_jwt_identity

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    user_id = get_jwt_identity()

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

@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    expense_data = [{'id': expense.id, 'amount': expense.amount, 'description': expense.description, 'date': expense.date, 'category': expense.category} for expense in expenses]
    return jsonify({'expenses': expense_data}), 200

@expense_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    data = request.get_json()
    expense = Expense.query.get_or_404(id)

    expense.amount = data.get('amount', expense.amount)
    expense.description = data.get('description', expense.description)
    expense.date = data.get('date', expense.date)
    expense.category = data.get('category', expense.category)

    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'}), 200

@expense_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'}), 200
