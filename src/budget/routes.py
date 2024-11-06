from flask import Blueprint, request, jsonify
from src.models import db, Budget
from flask_jwt_extended import jwt_required, get_jwt_identity

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/', methods=['POST'])
@jwt_required()
def add_budget():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_budget = Budget(
        category=data['category'],
        amount=data['amount'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        user_id=user_id
    )

    db.session.add(new_budget)
    db.session.commit()
    return jsonify({'message': 'Budget added successfully'}), 201

@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    user_id = get_jwt_identity()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    budget_data = [{'id': budget.id, 'category': budget.category, 'amount': budget.amount, 'start_date': budget.start_date, 'end_date': budget.end_date} for budget in budgets]
    return jsonify({'budgets': budget_data}), 200

@budget_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_budget(id):
    data = request.get_json()
    budget = Budget.query.get_or_404(id)

    budget.category = data.get('category', budget.category)
    budget.amount = data.get('amount', budget.amount)
    budget.start_date = data.get('start_date', budget.start_date)
    budget.end_date = data.get('end_date', budget.end_date)

    db.session.commit()
    return jsonify({'message': 'Budget updated successfully'}), 200

@budget_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    return jsonify({'message': 'Budget deleted successfully'}), 200
