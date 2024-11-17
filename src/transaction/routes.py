from flask import Blueprint, request, jsonify
from src.models import db, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity

transaction_bp = Blueprint('transaction', __name__)

# Helper function for error handling
def handle_error(e, message='An error occurred'):
    db.session.rollback()
    return jsonify({'message': message, 'error': str(e)}), 500

# POST - Add a Transaction
@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def add_transaction():
    data = request.get_json()
    user_id = get_jwt_identity()

    # Data validation
    if not data.get('amount') or not data.get('transaction_type') or not data.get('date'):
        return jsonify({'message': 'Missing required fields'}), 400

    # Ensure valid transaction_type
    if data['transaction_type'] not in ['income', 'expense']:
        return jsonify({'message': 'Invalid transaction type'}), 400

    try:
        new_transaction = Transaction(
            user_id=user_id,
            transaction_type=data['transaction_type'],
            description=data.get('description', ''),
            amount=data['amount'],
            date=data['date']
        )

        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added successfully'}), 201

    except Exception as e:
        return handle_error(e, 'Error occurred while adding transaction')

# GET - Retrieve Transactions for User (with filters and pagination)
@transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()

    # Filters and pagination parameters
    transaction_type = request.args.get('transaction_type', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        query = Transaction.query.filter_by(user_id=user_id)

        # Apply optional filters
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        if start_date and end_date:
            query = query.filter(Transaction.date.between(start_date, end_date))

        transactions = query.paginate(page, per_page, False)
        transaction_data = [{
            'id': transaction.id,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type,
            'description': transaction.description,
            'date': transaction.date
        } for transaction in transactions.items]

        return jsonify({
            'transactions': transaction_data,
            'total_pages': transactions.pages,
            'current_page': transactions.page
        }), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while retrieving transactions')

# PUT - Update Transaction (only for the owner)
@transaction_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    data = request.get_json()
    user_id = get_jwt_identity()

    # Fetch transaction entry
    transaction = Transaction.query.get_or_404(id)

    # Ensure the transaction belongs to the authenticated user
    if transaction.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        # Update fields if provided
        transaction.amount = data.get('amount', transaction.amount)
        transaction.transaction_type = data.get('transaction_type', transaction.transaction_type)
        transaction.description = data.get('description', transaction.description)
        transaction.date = data.get('date', transaction.date)

        # Ensure valid transaction_type if updated
        if transaction.transaction_type not in ['income', 'expense']:
            return jsonify({'message': 'Invalid transaction type'}), 400

        db.session.commit()
        return jsonify({'message': 'Transaction updated successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while updating transaction')

# DELETE - Delete Transaction (only for the owner)
@transaction_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()

    # Fetch transaction entry
    transaction = Transaction.query.get_or_404(id)

    # Ensure the transaction belongs to the authenticated user
    if transaction.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction deleted successfully'}), 200

    except Exception as e:
        return handle_error(e, 'Error occurred while deleting transaction')
