from flask import Blueprint, request, jsonify
from src.models import db, SavingsGoal
from flask_jwt_extended import jwt_required, get_jwt_identity

savings_goal_bp = Blueprint('savings_goal', __name__)

# Helper function for error handling
def handle_error(e, message='An error occurred'):
    db.session.rollback()
    return jsonify({'message': message, 'error': str(e)}), 500

# POST - Add Savings Goal
@savings_goal_bp.route('/', methods=['POST'])
@jwt_required()
def add_savings_goal():
    data = request.get_json()
    user_id = get_jwt_identity()

    # Data Validation
    if not data.get('goal_name') or not data.get('target_amount') or not data.get('deadline'):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
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

    except Exception as e:
        return handle_error(e, 'Error occurred while adding the savings goal')

# GET - Retrieve All Savings Goals for User (with pagination)
@savings_goal_bp.route('/', methods=['GET'])
@jwt_required()
def get_savings_goals():
    user_id = get_jwt_identity()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        goals = SavingsGoal.query.filter_by(user_id=user_id).paginate(page, per_page, False)
        goal_data = [{
            'id': goal.id, 'goal_name': goal.goal_name, 'target_amount': goal.target_amount, 
            'current_amount': goal.current_amount, 'deadline': goal.deadline
        } for goal in goals.items]

        return jsonify({
            'savings_goals': goal_data, 
            'total_pages': goals.pages, 
            'current_page': goals.page
        }), 200
    except Exception as e:
        return handle_error(e, 'Error occurred while retrieving savings goals')

# PUT - Update Savings Goal
@savings_goal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_savings_goal(id):
    data = request.get_json()
    user_id = get_jwt_identity()

    # Fetch goal
    goal = SavingsGoal.query.get_or_404(id)

    # Ensure the goal belongs to the authenticated user
    if goal.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        # Update fields if provided
        goal.goal_name = data.get('goal_name', goal.goal_name)
        goal.target_amount = data.get('target_amount', goal.target_amount)
        goal.current_amount = data.get('current_amount', goal.current_amount)
        goal.deadline = data.get('deadline', goal.deadline)

        db.session.commit()
        return jsonify({'message': 'Savings goal updated successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while updating the savings goal')

# DELETE - Delete Savings Goal
@savings_goal_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_savings_goal(id):
    user_id = get_jwt_identity()

    # Fetch goal
    goal = SavingsGoal.query.get_or_404(id)

    # Ensure the goal belongs to the authenticated user
    if goal.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Savings goal deleted successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while deleting the savings goal')
