from flask import Blueprint, request, jsonify
from src.models import db, SavingsGoal
from flask_jwt_extended import jwt_required, get_jwt_identity

savings_goal_bp = Blueprint('savings_goal', __name__)

@savings_goal_bp.route('/', methods=['POST'])
@jwt_required()
def add_savings_goal():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_goal = SavingsGoal(
        goal_name=data['goal_name'],
        target_amount=data['target_amount'],
        current_amount=data.get('current_amount', 0),
        deadline=data['deadline'],
        user_id=user_id
    )

    db.session.add(new_goal)
    db.session.commit()
    return jsonify({'message': 'Savings goal added successfully'}), 201

@savings_goal_bp.route('/', methods=['GET'])
@jwt_required()
def get_savings_goals():
    user_id = get_jwt_identity()
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    goal_data = [{'id': goal.id, 'goal_name': goal.goal_name, 'target_amount': goal.target_amount, 'current_amount': goal.current_amount, 'deadline': goal.deadline} for goal in goals]
    return jsonify({'savings_goals': goal_data}), 200

@savings_goal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_savings_goal(id):
    data = request.get_json()
    goal = SavingsGoal.query.get_or_404(id)

    goal.goal_name = data.get('goal_name', goal.goal_name)
    goal.target_amount = data.get('target_amount', goal.target_amount)
    goal.current_amount = data.get('current_amount', goal.current_amount)
    goal.deadline = data.get('deadline', goal.deadline)

    db.session.commit()
    return jsonify({'message': 'Savings goal updated successfully'}), 200

@savings_goal_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_savings_goal(id):
    goal = SavingsGoal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Savings goal deleted successfully'}), 200
