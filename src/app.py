from src import create_app
from src.users.routes import user_bp
from src.income.routes import income_bp
from src.expense.routes import expense_bp
from src.budget.routes import budget_bp
from src.savings_goal.routes import savings_goal_bp
from flask import jsonify
from flask_cors import CORS

app = create_app()

CORS(app) 

@app.get("/")
def hello():
    return jsonify({"message": "Welcome to the personal assistant api."})

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(income_bp, url_prefix='/income')
app.register_blueprint(expense_bp, url_prefix='/expense')
app.register_blueprint(budget_bp, url_prefix='/budget')
app.register_blueprint(savings_goal_bp, url_prefix='/savings-goal')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
