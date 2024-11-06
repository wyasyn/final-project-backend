from flask import Blueprint, request, jsonify
from src.models import db, Income
from flask_jwt_extended import jwt_required, get_jwt_identity

income_bp = Blueprint('income', __name__)

@income_bp.route('/', methods=['POST'])
@jwt_required()
def add_income():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_income = Income(
        amount=data['amount'],
        description=data.get('description', ''),
        date=data['date'],
        user_id=user_id
    )

    db.session.add(new_income)
    db.session.commit()
    return jsonify({'message': 'Income added successfully'}), 201

@income_bp.route('/', methods=['GET'])
@jwt_required()
def get_income():
    user_id = get_jwt_identity()
    incomes = Income.query.filter_by(user_id=user_id).all()
    income_data = [{'id': income.id, 'amount': income.amount, 'description': income.description, 'date': income.date} for income in incomes]
    return jsonify({'incomes': income_data}), 200

@income_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_income(id):
    data = request.get_json()
    income = Income.query.get_or_404(id)

    income.amount = data.get('amount', income.amount)
    income.description = data.get('description', income.description)
    income.date = data.get('date', income.date)

    db.session.commit()
    return jsonify({'message': 'Income updated successfully'}), 200

@income_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_income(id):
    income = Income.query.get_or_404(id)
    db.session.delete(income)
    db.session.commit()
    return jsonify({'message': 'Income deleted successfully'}), 200
