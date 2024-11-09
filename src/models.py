from src import db
from sqlalchemy import func
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import SignatureExpired
from flask import current_app
from typing import Dict

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    middle_name = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    career = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    # Relationships
    incomes = db.relationship('Income', backref='user', lazy=True)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy=True)

    def set_password(self, password: str) -> None:
        """Hashes and sets the password for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, str]:
        """Returns a dictionary representation of the user."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number,
            'career': self.career,
            'created_at': self.created_at
        }

    
    def get_reset_password_token(self):
        """Generate a password reset token."""
        try:
            # Generate token with unique user_id
            return current_app.serializer.dumps({'user_id': self.id}, salt='reset-password')
        except Exception as e:
            current_app.logger.error(f"Error generating token: {e}")
            raise


    @staticmethod
    def verify_reset_password_token(token):
        """Verify the password reset token."""
        try:
            # Load the token with a 10-minute expiration
            data = current_app.serializer.loads(token, salt='reset-password', max_age=600)
            return User.query.get(data['user_id'])
        except SignatureExpired:
            current_app.logger.warning("Token expired.")
            raise ValueError("The token has expired.")
        except Exception as e:
            current_app.logger.error(f"Error verifying token: {e}")
            raise ValueError("Invalid token.")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"

class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, str]:
        """Returns a dictionary representation of the income entry."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'amount': self.amount,
            'date': self.date
        }

    def __repr__(self) -> str:
        return f"<Income {self.source}: {self.amount}>"

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, str]:
        """Returns a dictionary representation of the expense entry."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'date': self.date
        }

    def __repr__(self) -> str:
        return f"<Expense {self.category}: {self.amount}>"

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def to_dict(self) -> Dict[str, str]:
        """Returns a dictionary representation of the budget entry."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'amount': self.amount,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    def __repr__(self) -> str:
        return f"<Budget {self.category}: {self.amount}>"

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    def calculate_progress(self) -> float:
        """Calculates the progress towards the savings goal as a percentage."""
        return (self.current_amount / self.target_amount * 100) if self.target_amount else 0

    def to_dict(self) -> Dict[str, str]:
        """Returns a dictionary representation of the savings goal."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_name': self.goal_name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'deadline': self.deadline,
            'created_at': self.created_at,
            'progress': self.calculate_progress()
        }

    def __repr__(self) -> str:
        return f"<SavingsGoal {self.goal_name}: Target={self.target_amount}, Current={self.current_amount}>"
